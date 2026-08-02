"""Tests for the dashboard card, the history pages and the on-demand generation."""

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from ai.models import AIAnalysis


def body_of(response):
    return response.content.decode()


def messages_of(response):
    return ' '.join(str(message) for message in response.context['messages'])


@pytest.fixture
def analysis(user):
    return AIAnalysis.objects.create(
        user=user,
        status='success',
        summary='Você fechou o mês com sobra.',
        insights=['Alimentação levou 80% das saídas.', 'Entradas estáveis.', 'Saldo positivo.'],
        tips=['Defina um teto para Alimentação.', 'Guarde a sobra.', 'Revise assinaturas.'],
        health_score=72,
        health_label='good',
        model_name='deepseek-chat',
    )


@pytest.mark.django_db
class TestDashboardCard:
    def test_shows_the_latest_successful_analysis(self, client, user, ai_enabled, analysis):
        client.force_login(user)
        body = body_of(client.get(reverse('dashboard')))

        assert 'Análise Inteligente' in body
        assert analysis.summary in body
        assert 'Alimentação levou 80% das saídas.' in body
        assert 'Defina um teto para Alimentação.' in body
        assert '72' in body

    def test_empty_state_invites_the_first_analysis(self, client, user, ai_enabled):
        client.force_login(user)
        body = body_of(client.get(reverse('dashboard')))

        assert 'Análise Inteligente' in body
        assert 'ainda não tem uma análise' in body
        assert 'Gerar primeira análise' in body

    def test_error_state_shows_a_friendly_message(self, client, user, ai_enabled):
        AIAnalysis.objects.create(
            user=user, status='error', error_message='Credencial da API de IA inválida.'
        )
        client.force_login(user)
        body = body_of(client.get(reverse('dashboard')))

        assert 'Credencial da API de IA inválida.' in body

    def test_a_failed_run_keeps_the_previous_analysis_visible(
        self, client, user, ai_enabled, analysis
    ):
        # Backdated explicitly: created back to back, both rows can land on the
        # same clock tick and the ordering by created_at becomes ambiguous.
        AIAnalysis.objects.filter(pk=analysis.pk).update(
            created_at=timezone.now() - datetime.timedelta(minutes=5)
        )
        AIAnalysis.objects.create(user=user, status='error', error_message='Falhou de novo.')
        client.force_login(user)
        body = body_of(client.get(reverse('dashboard')))

        assert analysis.summary in body
        assert 'A última tentativa de gerar uma análise falhou' in body

    def test_card_is_hidden_when_the_feature_is_off(self, client, user, settings, analysis):
        settings.AI_ANALYSIS_ENABLED = False
        client.force_login(user)
        body = body_of(client.get(reverse('dashboard')))

        assert 'Análise Inteligente' not in body
        assert analysis.summary not in body

    def test_another_users_analysis_never_appears(self, client, user, other_user, ai_enabled):
        AIAnalysis.objects.create(
            user=other_user, status='success', summary='Diagnóstico do outro usuário.'
        )
        client.force_login(user)
        body = body_of(client.get(reverse('dashboard')))

        assert 'Diagnóstico do outro usuário.' not in body
        assert 'ainda não tem uma análise' in body

    def test_dashboard_survives_an_ai_failure(self, client, user, ai_enabled, monkeypatch):
        def boom(_user):
            raise RuntimeError('banco fora do ar')

        monkeypatch.setattr('ai.services.analysis_panel_context', boom)
        client.force_login(user)
        response = client.get(reverse('dashboard'))

        assert response.status_code == 200
        assert 'Análise Inteligente' not in body_of(response)
        # The rest of the dashboard keeps working
        assert 'Saldo Total' in body_of(response)


@pytest.mark.django_db
class TestAnalysisListView:
    def test_requires_login(self, client):
        response = client.get(reverse('ai:analysis_list'))

        assert response.status_code == 302
        assert '/login' in response.url

    def test_lists_only_the_logged_users_analyses(
        self, client, user, other_user, ai_enabled, analysis
    ):
        AIAnalysis.objects.create(
            user=other_user, status='success', summary='Diagnóstico do outro usuário.'
        )
        client.force_login(user)
        response = client.get(reverse('ai:analysis_list'))

        assert list(response.context['analyses']) == [analysis]
        assert 'Diagnóstico do outro usuário.' not in body_of(response)

    def test_paginates_by_ten(self, client, user, ai_enabled):
        for index in range(11):
            AIAnalysis.objects.create(user=user, status='error', error_message=f'falha {index}')
        client.force_login(user)
        response = client.get(reverse('ai:analysis_list'))

        assert len(response.context['analyses']) == 10
        assert response.context['page_obj'].paginator.num_pages == 2

    def test_empty_state(self, client, user, ai_enabled):
        client.force_login(user)

        assert 'ainda não gerou nenhuma análise' in body_of(
            client.get(reverse('ai:analysis_list'))
        )


@pytest.mark.django_db
class TestAnalysisDetailView:
    def test_requires_login(self, client, analysis):
        response = client.get(reverse('ai:analysis_detail', args=[analysis.pk]))

        assert response.status_code == 302
        assert '/login' in response.url

    def test_renders_the_analysis(self, client, user, ai_enabled, analysis):
        client.force_login(user)
        body = body_of(client.get(reverse('ai:analysis_detail', args=[analysis.pk])))

        assert analysis.summary in body
        assert 'Guarde a sobra.' in body
        assert 'deepseek-chat' in body

    def test_another_users_analysis_returns_404(self, client, user, other_user, ai_enabled):
        foreign = AIAnalysis.objects.create(user=other_user, status='success', summary='alheia')
        client.force_login(user)

        assert client.get(reverse('ai:analysis_detail', args=[foreign.pk])).status_code == 404


@pytest.mark.django_db
class TestGenerateAnalysisView:
    def test_requires_login(self, client):
        response = client.post(reverse('ai:generate'))

        assert response.status_code == 302
        assert '/login' in response.url

    def test_rejects_get(self, client, user, ai_enabled):
        client.force_login(user)

        assert client.get(reverse('ai:generate')).status_code == 405

    def test_generates_and_redirects_to_the_dashboard(
        self, client, user_with_history, ai_enabled, fake_agent
    ):
        client.force_login(user_with_history)
        response = client.post(reverse('ai:generate'))

        assert response.url == reverse('dashboard')
        analysis = AIAnalysis.objects.get(user=user_with_history)
        assert analysis.status == 'success'
        assert len(fake_agent.calls) == 1

    def test_success_message(self, client, user_with_history, ai_enabled, fake_agent):
        client.force_login(user_with_history)
        response = client.post(reverse('ai:generate'), follow=True)

        assert 'Nova análise gerada com sucesso.' in messages_of(response)

    def test_reports_the_failure_without_breaking(
        self, client, user, ai_enabled, monkeypatch
    ):
        def boom(_user):
            raise ConnectionError('rede fora')

        monkeypatch.setattr('ai.services.build_finance_agent', boom)
        client.force_login(user)
        response = client.post(reverse('ai:generate'), follow=True)

        assert response.status_code == 200
        assert AIAnalysis.objects.get(user=user).status == 'error'
        assert 'Não foi possível concluir a análise' in messages_of(response)

    def test_blocked_when_the_feature_is_off(self, client, user, settings, monkeypatch):
        settings.AI_ANALYSIS_ENABLED = False
        monkeypatch.setattr(
            'ai.services.run_analysis_for_user',
            lambda _user: pytest.fail('não deveria executar o agente'),
        )
        client.force_login(user)
        response = client.post(reverse('ai:generate'), follow=True)

        assert AIAnalysis.objects.count() == 0
        assert 'indisponível' in messages_of(response)

    def test_minimum_interval_blocks_the_second_request(
        self, client, user, ai_enabled, fake_agent, analysis
    ):
        client.force_login(user)
        response = client.post(reverse('ai:generate'), follow=True)

        assert fake_agent.calls == []
        assert AIAnalysis.objects.count() == 1
        assert 'Tente novamente em 15 minutos' in messages_of(response)

    def test_returns_to_the_history_when_asked(
        self, client, user_with_history, ai_enabled, fake_agent
    ):
        client.force_login(user_with_history)
        response = client.post(
            reverse('ai:generate'), {'next': reverse('ai:analysis_list')}
        )

        assert response.url == reverse('ai:analysis_list')

    def test_ignores_an_external_redirect(
        self, client, user_with_history, ai_enabled, fake_agent
    ):
        client.force_login(user_with_history)
        response = client.post(
            reverse('ai:generate'), {'next': 'https://exemplo-malicioso.com/'}
        )

        assert response.url == reverse('dashboard')


@pytest.mark.django_db
class TestNavigation:
    def test_sidebar_links_to_the_history(self, client, user, ai_enabled):
        client.force_login(user)
        body = body_of(client.get(reverse('dashboard')))

        # Desktop sidebar and mobile drawer
        assert body.count(f'href="{reverse("ai:analysis_list")}"') >= 2
