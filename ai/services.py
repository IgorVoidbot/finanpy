"""Execution of the finance agent and persistence of its result.

`run_analysis_for_user()` is the single entry point used by the view and by the
batch management command. It never raises: any failure — network, credentials,
rate limit, timeout, output outside the schema — becomes an `AIAnalysis` with
`status='error'`, so the dashboard degrades to the error card instead of
breaking (RNF13 in PRD.md).
"""

import logging
import math
import time

from django.conf import settings
from django.utils import timezone
from langchain_core.messages import AIMessage
from langgraph.errors import GraphRecursionError
from pydantic import ValidationError

from ai.agent import (
    AgentError,
    AgentNotConfigured,
    AgentOutputError,
    build_finance_agent,
    build_run_config,
    is_agent_available,
)
from ai.models import AIAnalysis
from ai.prompts import build_analysis_request


logger = logging.getLogger(__name__)

MAX_ERROR_MESSAGE_LENGTH = 500

REDACTED = '[credencial omitida]'

GENERIC_ERROR = 'Não foi possível concluir a análise. Tente novamente em alguns minutos.'

# Friendly Brazilian Portuguese message per failure class. Order matters:
# the first entry whose exception name matches is the one used.
ERROR_MESSAGES = [
    ('AuthenticationError', 'Credencial da API de IA inválida ou expirada.'),
    ('PermissionDeniedError', 'A credencial da API de IA não tem permissão para este modelo.'),
    ('RateLimitError', 'Limite de uso da API de IA atingido. Tente novamente mais tarde.'),
    ('APITimeoutError', 'A análise demorou mais que o tempo limite e foi interrompida.'),
    ('APIConnectionError', 'Não foi possível conectar à API de IA.'),
    ('BadRequestError', 'A API de IA recusou a requisição da análise.'),
    ('InternalServerError', 'A API de IA está indisponível no momento.'),
]


def is_enabled():
    """Whether analyses can be generated at all in this installation."""
    return is_agent_available()


def cooldown_remaining_minutes(user):
    """Minutes left before the user may generate another analysis.

    Every run counts — including the ones that failed — because a failed run
    still spends an API call.
    """
    interval = settings.AI_ANALYSIS_MIN_INTERVAL_MINUTES
    if interval <= 0:
        return 0

    last_created_at = (
        AIAnalysis.objects.for_user(user)
        .values_list('created_at', flat=True)
        .first()
    )
    if last_created_at is None:
        return 0

    elapsed = (timezone.now() - last_created_at).total_seconds() / 60
    return max(0, math.ceil(interval - elapsed))


def can_generate_analysis(user):
    """Returns `(allowed, remaining_minutes)` for the on-demand generation."""
    remaining = cooldown_remaining_minutes(user)
    return remaining == 0, remaining


def run_analysis_for_user(user):
    """Runs the agent for one user and stores the outcome.

    Returns the persisted `AIAnalysis`, or `None` when the feature is turned
    off — in that case nothing is stored and no API call is made.
    """
    if not is_enabled():
        logger.info('AI analysis is disabled; skipping run for user %s', user.pk)
        return None

    months = settings.AI_ANALYSIS_MONTHS_WINDOW
    started_at = time.monotonic()

    try:
        agent = build_finance_agent(user)
        result = agent.invoke(
            {'messages': [{'role': 'user', 'content': build_analysis_request(months)}]},
            config=build_run_config(),
        )
        analysis = result.get('structured_response')
        if analysis is None:
            raise AgentOutputError(
                'the run ended without a structured analysis '
                '(iteration cap reached or invalid output)'
            )
    except Exception as exc:
        return _store_failure(user, exc, _elapsed_ms(started_at))

    return _store_success(user, analysis, result, _elapsed_ms(started_at))


def _elapsed_ms(started_at):
    return int((time.monotonic() - started_at) * 1000)


def _collect_usage(result):
    """Sums token usage and counts model calls across the run's messages."""
    usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0, 'iterations': 0}

    for message in result.get('messages', []):
        if not isinstance(message, AIMessage):
            continue
        usage['iterations'] += 1
        metadata = message.usage_metadata or {}
        usage['prompt_tokens'] += metadata.get('input_tokens', 0)
        usage['completion_tokens'] += metadata.get('output_tokens', 0)
        usage['total_tokens'] += metadata.get('total_tokens', 0)

    return usage


def _store_success(user, analysis, result, duration_ms):
    usage = _collect_usage(result)
    return AIAnalysis.objects.create(
        user=user,
        status='success',
        summary=analysis.summary,
        insights=analysis.insights,
        tips=analysis.tips,
        health_score=analysis.health_score,
        health_label=analysis.health_label,
        period_start=analysis.period_start,
        period_end=analysis.period_end,
        model_name=settings.DEEPSEEK_MODEL,
        duration_ms=duration_ms,
        **usage,
    )


def _store_failure(user, exc, duration_ms):
    # The technical detail goes to the log only; the user sees the friendly text.
    logger.error(
        'AI analysis failed for user %s: %s',
        user.pk,
        _redact(f'{type(exc).__name__}: {exc}'),
        exc_info=True,
    )
    return AIAnalysis.objects.create(
        user=user,
        status='error',
        error_message=_friendly_error(exc),
        model_name=settings.DEEPSEEK_MODEL,
        duration_ms=duration_ms,
    )


def _friendly_error(exc):
    """Maps an exception to a short Brazilian Portuguese message."""
    if isinstance(exc, AgentNotConfigured):
        return 'A análise de IA não está configurada neste ambiente.'
    if isinstance(exc, GraphRecursionError):
        return 'A análise excedeu o número máximo de etapas permitidas.'
    if isinstance(exc, (AgentOutputError, ValidationError)):
        return 'A IA devolveu uma resposta fora do formato esperado.'
    if isinstance(exc, AgentError):
        return GENERIC_ERROR

    names = {klass.__name__ for klass in type(exc).__mro__}
    for name, message in ERROR_MESSAGES:
        if name in names:
            return message
    return GENERIC_ERROR


def _redact(text):
    """Removes the API key from any text before it reaches a log or the database."""
    key = settings.DEEPSEEK_API_KEY
    text = str(text)
    if key:
        text = text.replace(key, REDACTED)
    return text[:MAX_ERROR_MESSAGE_LENGTH]
