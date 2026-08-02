"""Assembly of the LangChain agent that analyses one user's finances.

APIs used (LangChain 1.3.14 / langchain-deepseek 1.1.0), checked against the
current documentation before writing this module:

- `langchain.agents.create_agent(model, tools, system_prompt=..., response_format=...,
  middleware=...)` — builds the agent graph.
- `langchain.agents.structured_output.ToolStrategy(schema)` — final answer comes
  back as a tool call validated against a Pydantic schema. DeepSeek has no native
  structured-output mode, so the tool strategy is the portable option; on a
  schema violation it feeds the error back to the model, which retries.
- `langchain.agents.middleware.ModelCallLimitMiddleware(run_limit=...)` — caps how
  many times the model is called in a single run.
- `langchain_deepseek.ChatDeepSeek(model=..., api_key=..., temperature=...,
  timeout=..., max_retries=...)`.
- `agent.invoke(payload, config={'recursion_limit': ...})` — hard stop for the
  graph, raising `langgraph.errors.GraphRecursionError`.
"""

import logging

from django.conf import settings
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.agents.structured_output import ToolStrategy
from langchain_deepseek import ChatDeepSeek

from ai.prompts import SYSTEM_PROMPT
from ai.schemas import FinancialAnalysis
from ai.tools import build_tools


logger = logging.getLogger(__name__)

# Low enough to keep the numbers stable between runs, not zero so the wording
# does not become repetitive across analyses of the same user.
MODEL_TEMPERATURE = 0.2

# A single retry keeps a transient network hiccup from failing the whole run
# without blowing past AI_AGENT_TIMEOUT_SECONDS.
MODEL_MAX_RETRIES = 1


class AgentError(Exception):
    """Base error for problems building or running the finance agent."""


class AgentNotConfigured(AgentError):
    """Raised when the agent is disabled or has no API key available."""


class AgentOutputError(AgentError):
    """Raised when the run ends without a valid structured analysis."""


def is_agent_available():
    """Tells whether the feature flag and the API key allow a run."""
    return bool(settings.AI_ANALYSIS_ENABLED and settings.DEEPSEEK_API_KEY)


def build_chat_model():
    """Builds the DeepSeek chat model from the project settings."""
    if not settings.DEEPSEEK_API_KEY:
        raise AgentNotConfigured('DEEPSEEK_API_KEY is not configured')

    return ChatDeepSeek(
        model=settings.DEEPSEEK_MODEL,
        api_key=settings.DEEPSEEK_API_KEY,
        temperature=MODEL_TEMPERATURE,
        timeout=settings.AI_AGENT_TIMEOUT_SECONDS,
        max_retries=MODEL_MAX_RETRIES,
    )


def build_finance_agent(user):
    """Builds the agent bound to a single user.

    The tools come from `build_tools(user)`, which fixes the user server-side:
    the model never receives — and cannot ask for — a user identifier, so a run
    can only ever read the data of the user passed in here (RF09.5 in PRD.md).
    """
    return create_agent(
        model=build_chat_model(),
        tools=build_tools(user),
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(FinancialAnalysis),
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=settings.AI_AGENT_MAX_ITERATIONS,
                exit_behavior='end',
            ),
        ],
    )


# Super-steps the graph spends on one iteration of the loop. The middleware
# hooks are nodes too, so a full cycle is
# `before_model` → `model` → `after_model` → `tools`.
GRAPH_STEPS_PER_ITERATION = 4

# Room for `__start__`, the final model call that answers without calling a
# tool, and its `after_model` hook.
GRAPH_STEPS_MARGIN = 6


def build_run_config():
    """Graph-level safety net for the iteration cap.

    The middleware is what should stop the loop — it ends the run cleanly,
    while blowing the recursion limit aborts it with `GraphRecursionError`.
    So this limit is deliberately set above what `AI_AGENT_MAX_ITERATIONS`
    iterations can spend, and only catches a loop the middleware misses.
    """
    return {
        'recursion_limit': (
            GRAPH_STEPS_PER_ITERATION * settings.AI_AGENT_MAX_ITERATIONS
            + GRAPH_STEPS_MARGIN
        )
    }
