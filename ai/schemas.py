"""Structured output schema returned by the finance agent.

The field descriptions are part of the prompt: the model reads them to decide
what to write in each field, so they double as instructions.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


HealthLabel = Literal['critical', 'attention', 'good', 'excellent']


class FinancialAnalysis(BaseModel):
    """Diagnosis of one user's finances over a period, in Brazilian Portuguese."""

    summary: str = Field(
        description=(
            'General diagnosis of the period, 2 to 4 sentences, written in '
            'Brazilian Portuguese. Says plainly when there is not enough data.'
        ),
    )
    insights: list[str] = Field(
        min_length=3,
        max_length=5,
        description=(
            'Between 3 and 5 objective observations in Brazilian Portuguese, '
            'each one backed by a concrete number taken from the tools.'
        ),
    )
    tips: list[str] = Field(
        min_length=3,
        max_length=5,
        description=(
            'Between 3 and 5 actionable recommendations in Brazilian '
            'Portuguese, specific to the situation observed — no generic advice.'
        ),
    )
    health_score: int = Field(
        ge=0,
        le=100,
        description='Financial health score from 0 to 100, consistent with health_label.',
    )
    health_label: HealthLabel = Field(
        description=(
            'Score range: critical (0-39), attention (40-59), good (60-79), '
            'excellent (80-100).'
        ),
    )
    period_start: date = Field(description='First day of the analysed window (ISO 8601).')
    period_end: date = Field(description='Last day of the analysed window (ISO 8601).')

    @model_validator(mode='after')
    def check_period(self):
        if self.period_start > self.period_end:
            raise ValueError('period_start must not be later than period_end')
        return self

    @model_validator(mode='after')
    def check_score_matches_label(self):
        """Keeps score and label coherent — the badge colour comes from the label."""
        ranges = {
            'critical': (0, 39),
            'attention': (40, 59),
            'good': (60, 79),
            'excellent': (80, 100),
        }
        low, high = ranges[self.health_label]
        if not low <= self.health_score <= high:
            raise ValueError(
                f'health_score {self.health_score} is outside the '
                f'{self.health_label} range ({low}-{high})'
            )
        return self
