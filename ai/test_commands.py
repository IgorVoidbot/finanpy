"""Tests for the `run_ai_analysis` management command."""

from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from ai.models import AIAnalysis


def run(*args):
    output = StringIO()
    call_command('run_ai_analysis', *args, stdout=output, stderr=output)
    return output.getvalue()


def store_success(user):
    return AIAnalysis.objects.create(
        user=user, status='success', summary='ok', health_score=70, health_label='good'
    )


@pytest.mark.django_db
class TestRunAiAnalysisCommand:
    def test_requires_the_feature_to_be_enabled(self, user, settings):
        settings.AI_ANALYSIS_ENABLED = False

        with pytest.raises(CommandError):
            run()

    def test_generates_one_analysis_per_active_user(
        self, user, other_user, ai_enabled, monkeypatch
    ):
        monkeypatch.setattr('ai.services.run_analysis_for_user', store_success)
        output = run()

        assert AIAnalysis.objects.filter(user=user).count() == 1
        assert AIAnalysis.objects.filter(user=other_user).count() == 1
        assert '2 usuário(s) processados' in output
        assert 'sucessos: 2' in output

    def test_runs_the_whole_path_with_the_agent_double(
        self, user_with_history, ai_enabled, fake_agent
    ):
        run()

        analysis = AIAnalysis.objects.get(user=user_with_history)
        assert analysis.status == 'success'
        assert analysis.health_score == 72

    def test_skips_inactive_users(self, user, other_user, ai_enabled, monkeypatch):
        other_user.is_active = False
        other_user.save()
        monkeypatch.setattr('ai.services.run_analysis_for_user', store_success)
        run()

        assert AIAnalysis.objects.filter(user=other_user).count() == 0

    def test_user_option_restricts_to_one_user(self, user, other_user, ai_enabled, monkeypatch):
        monkeypatch.setattr('ai.services.run_analysis_for_user', store_success)
        run('--user', other_user.email)

        assert AIAnalysis.objects.count() == 1
        assert AIAnalysis.objects.first().user == other_user

    def test_unknown_user_option_fails_loudly(self, user, ai_enabled):
        with pytest.raises(CommandError):
            run('--user', 'ninguem@example.com')

    def test_skip_empty_ignores_users_without_transactions(
        self, user_with_history, other_user, ai_enabled, monkeypatch
    ):
        monkeypatch.setattr('ai.services.run_analysis_for_user', store_success)
        run('--skip-empty')

        assert AIAnalysis.objects.count() == 1
        assert AIAnalysis.objects.first().user == user_with_history

    def test_dry_run_lists_without_calling_the_api(
        self, user, other_user, settings, monkeypatch
    ):
        settings.AI_ANALYSIS_ENABLED = False
        monkeypatch.setattr(
            'ai.services.run_analysis_for_user',
            lambda _user: pytest.fail('não deveria chamar a API'),
        )
        output = run('--dry-run')

        assert user.email in output
        assert other_user.email in output
        assert AIAnalysis.objects.count() == 0

    def test_a_failing_user_does_not_stop_the_batch(
        self, user, other_user, ai_enabled, monkeypatch
    ):
        def flaky(target):
            if target == user:
                raise RuntimeError('banco fora do ar')
            return store_success(target)

        monkeypatch.setattr('ai.services.run_analysis_for_user', flaky)
        output = run()

        assert AIAnalysis.objects.filter(user=other_user).count() == 1
        assert 'sucessos: 1' in output
        assert 'falhas: 1' in output

    def test_an_error_analysis_counts_as_a_failure(self, user, ai_enabled, monkeypatch):
        monkeypatch.setattr(
            'ai.services.run_analysis_for_user',
            lambda target: AIAnalysis.objects.create(
                user=target, status='error', error_message='Credencial inválida.'
            ),
        )
        output = run()

        assert 'falhas: 1' in output
        assert 'Credencial inválida.' in output
