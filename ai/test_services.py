"""Tests for the service that runs the agent and stores the analysis."""

import datetime

import pytest
from django.utils import timezone
from langgraph.errors import GraphRecursionError

from ai import services
from ai.agent import AgentNotConfigured
from ai.models import AIAnalysis


def fail_with(exception):
    """Builds a `build_finance_agent` replacement that always blows up."""

    def build(_user):
        raise exception

    return build


@pytest.mark.django_db
class TestRunAnalysis:
    def test_success_persists_the_structured_output(
        self, user_with_history, ai_enabled, fake_agent, fake_analysis
    ):
        analysis = services.run_analysis_for_user(user_with_history)

        assert analysis.status == 'success'
        assert analysis.user == user_with_history
        assert analysis.summary == fake_analysis.summary
        assert analysis.insights == fake_analysis.insights
        assert analysis.tips == fake_analysis.tips
        assert analysis.health_score == 72
        assert analysis.health_label == 'good'
        assert analysis.period_start == fake_analysis.period_start
        assert analysis.period_end == fake_analysis.period_end
        assert analysis.error_message == ''

    def test_success_records_the_execution_metadata(
        self, user_with_history, ai_enabled, fake_agent
    ):
        analysis = services.run_analysis_for_user(user_with_history)

        assert analysis.model_name == 'deepseek-chat'
        assert analysis.iterations == 2
        assert analysis.prompt_tokens == 200
        assert analysis.completion_tokens == 40
        assert analysis.total_tokens == 240
        assert analysis.duration_ms >= 0

    def test_the_run_is_capped_by_the_iteration_setting(
        self, user_with_history, ai_enabled, fake_agent
    ):
        ai_enabled.AI_AGENT_MAX_ITERATIONS = 4
        services.run_analysis_for_user(user_with_history)

        assert fake_agent.calls[0]['config'] == {'recursion_limit': 10}

    def test_disabled_flag_does_not_call_the_agent(self, user, settings, monkeypatch):
        settings.AI_ANALYSIS_ENABLED = False
        monkeypatch.setattr(
            'ai.services.build_finance_agent', fail_with(AssertionError('não deveria montar'))
        )

        assert services.run_analysis_for_user(user) is None
        assert AIAnalysis.objects.count() == 0

    def test_missing_api_key_disables_the_service(self, user, settings):
        settings.AI_ANALYSIS_ENABLED = True
        settings.DEEPSEEK_API_KEY = ''

        assert services.is_enabled() is False
        assert services.run_analysis_for_user(user) is None


@pytest.mark.django_db
class TestRunAnalysisFailures:
    def test_api_failure_becomes_an_error_record(self, user, ai_enabled, monkeypatch):
        monkeypatch.setattr(
            'ai.services.build_finance_agent', fail_with(ConnectionError('rede fora'))
        )

        analysis = services.run_analysis_for_user(user)

        assert analysis.status == 'error'
        assert analysis.error_message
        assert analysis.health_score is None
        assert AIAnalysis.objects.count() == 1

    def test_iteration_cap_becomes_an_error_record(self, user, ai_enabled, monkeypatch):
        monkeypatch.setattr(
            'ai.services.build_finance_agent', fail_with(GraphRecursionError('sem saída'))
        )

        analysis = services.run_analysis_for_user(user)

        assert analysis.status == 'error'
        assert 'etapas' in analysis.error_message

    def test_missing_structured_output_becomes_an_error_record(
        self, user, ai_enabled, monkeypatch
    ):
        class EmptyAgent:
            def invoke(self, payload, config=None):
                return {'messages': []}

        monkeypatch.setattr('ai.services.build_finance_agent', lambda _user: EmptyAgent())

        analysis = services.run_analysis_for_user(user)

        assert analysis.status == 'error'
        assert 'formato' in analysis.error_message

    def test_configuration_error_becomes_an_error_record(self, user, ai_enabled, monkeypatch):
        monkeypatch.setattr(
            'ai.services.build_finance_agent', fail_with(AgentNotConfigured('sem chave'))
        )

        analysis = services.run_analysis_for_user(user)

        assert analysis.status == 'error'
        assert 'configurada' in analysis.error_message

    def test_the_api_key_never_reaches_the_stored_message(self, user, ai_enabled, monkeypatch):
        key = ai_enabled.DEEPSEEK_API_KEY
        monkeypatch.setattr(
            'ai.services.build_finance_agent',
            fail_with(RuntimeError(f'401 usando a chave {key}')),
        )

        analysis = services.run_analysis_for_user(user)

        assert key not in analysis.error_message

    def test_a_failure_during_the_run_never_propagates(self, user, ai_enabled, monkeypatch):
        class ExplodingAgent:
            def invoke(self, payload, config=None):
                raise TimeoutError('a chamada demorou demais')

        monkeypatch.setattr('ai.services.build_finance_agent', lambda _user: ExplodingAgent())

        # No pytest.raises here on purpose: the service must swallow everything.
        assert services.run_analysis_for_user(user).status == 'error'


@pytest.mark.django_db
class TestCooldown:
    def test_no_previous_analysis_allows_generation(self, user, ai_enabled):
        assert services.can_generate_analysis(user) == (True, 0)

    def test_recent_analysis_blocks_generation(self, user, ai_enabled):
        AIAnalysis.objects.create(user=user, status='success', summary='ok')

        allowed, remaining = services.can_generate_analysis(user)

        assert allowed is False
        assert remaining == 15

    def test_a_failed_run_also_counts(self, user, ai_enabled):
        AIAnalysis.objects.create(user=user, status='error', error_message='falhou')

        assert services.can_generate_analysis(user)[0] is False

    def test_old_analysis_does_not_block(self, user, ai_enabled):
        analysis = AIAnalysis.objects.create(user=user, status='success', summary='ok')
        AIAnalysis.objects.filter(pk=analysis.pk).update(
            created_at=timezone.now() - datetime.timedelta(minutes=30)
        )

        assert services.can_generate_analysis(user) == (True, 0)

    def test_another_users_analysis_does_not_block(self, user, other_user, ai_enabled):
        AIAnalysis.objects.create(user=other_user, status='success', summary='ok')

        assert services.can_generate_analysis(user) == (True, 0)

    def test_zero_interval_disables_the_cooldown(self, user, ai_enabled):
        ai_enabled.AI_ANALYSIS_MIN_INTERVAL_MINUTES = 0
        AIAnalysis.objects.create(user=user, status='success', summary='ok')

        assert services.can_generate_analysis(user) == (True, 0)


@pytest.mark.django_db
class TestPanelContext:
    def test_disabled_returns_only_the_flag(self, user, settings):
        settings.AI_ANALYSIS_ENABLED = False

        assert services.analysis_panel_context(user) == {'ai_analysis_enabled': False}

    def test_empty_state(self, user, ai_enabled):
        context = services.analysis_panel_context(user)

        assert context['ai_analysis_enabled'] is True
        assert context['latest_ai_analysis'] is None
        assert context['last_ai_analysis'] is None
        assert context['ai_cooldown_minutes'] == 0

    def test_falls_back_to_the_previous_success_after_a_failure(self, user, ai_enabled):
        success = AIAnalysis.objects.create(user=user, status='success', summary='ok')
        # Backdated explicitly: created back to back, both rows can land on the
        # same clock tick and the ordering by created_at becomes ambiguous.
        AIAnalysis.objects.filter(pk=success.pk).update(
            created_at=timezone.now() - datetime.timedelta(minutes=5)
        )
        failure = AIAnalysis.objects.create(user=user, status='error', error_message='falhou')

        context = services.analysis_panel_context(user)

        assert context['latest_ai_analysis'] == success
        assert context['last_ai_analysis'] == failure

    def test_ignores_other_users(self, user, other_user, ai_enabled):
        AIAnalysis.objects.create(user=other_user, status='success', summary='do outro')

        context = services.analysis_panel_context(user)

        assert context['latest_ai_analysis'] is None
        assert context['last_ai_analysis'] is None
