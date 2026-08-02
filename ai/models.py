from django.conf import settings
from django.db import models


STATUS_CHOICES = [
    ('success', 'Sucesso'),
    ('error', 'Erro'),
]

HEALTH_LABEL_CHOICES = [
    ('critical', 'Crítica'),
    ('attention', 'Atenção'),
    ('good', 'Boa'),
    ('excellent', 'Excelente'),
]

# Tailwind classes by health label (see section 9.10 of PRD.md)
HEALTH_COLOR_CLASSES = {
    'critical': 'text-rose-400 bg-rose-500/10 border-rose-500/30',
    'attention': 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    'good': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    'excellent': 'text-violet-400 bg-violet-500/10 border-violet-500/30',
}

DEFAULT_HEALTH_COLOR_CLASS = 'text-gray-400 bg-gray-500/10 border-gray-500/30'

# Text colour alone, for the score number displayed next to the badge
HEALTH_TEXT_CLASSES = {
    'critical': 'text-rose-400',
    'attention': 'text-amber-400',
    'good': 'text-emerald-400',
    'excellent': 'text-violet-400',
}

DEFAULT_HEALTH_TEXT_CLASS = 'text-gray-400'


class AIAnalysisQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def successful(self):
        return self.filter(status='success')


class AIAnalysisManager(models.Manager.from_queryset(AIAnalysisQuerySet)):
    def latest_success_for(self, user):
        """Returns the most recent successful analysis of a user, or None."""
        return self.for_user(user).successful().first()


class AIAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_analyses',
        verbose_name='Usuário',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='Situação',
    )
    summary = models.TextField(blank=True, verbose_name='Resumo')
    insights = models.JSONField(default=list, blank=True, verbose_name='Insights')
    tips = models.JSONField(default=list, blank=True, verbose_name='Dicas')
    health_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Índice de saúde financeira',
    )
    health_label = models.CharField(
        max_length=20,
        choices=HEALTH_LABEL_CHOICES,
        blank=True,
        verbose_name='Classificação da saúde financeira',
    )
    period_start = models.DateField(
        null=True,
        blank=True,
        verbose_name='Início do período analisado',
    )
    period_end = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fim do período analisado',
    )
    model_name = models.CharField(max_length=50, blank=True, verbose_name='Modelo')
    prompt_tokens = models.PositiveIntegerField(default=0, verbose_name='Tokens de entrada')
    completion_tokens = models.PositiveIntegerField(default=0, verbose_name='Tokens de saída')
    total_tokens = models.PositiveIntegerField(default=0, verbose_name='Tokens totais')
    duration_ms = models.PositiveIntegerField(default=0, verbose_name='Duração (ms)')
    iterations = models.PositiveSmallIntegerField(default=0, verbose_name='Iterações')
    error_message = models.TextField(blank=True, verbose_name='Mensagem de erro')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    objects = AIAnalysisManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='ai_analysis_user_recent'),
        ]
        verbose_name = 'Análise de IA'
        verbose_name_plural = 'Análises de IA'

    def __str__(self):
        return f'Análise de {self.user} em {self.created_at:%d/%m/%Y %H:%M}'

    @property
    def is_success(self):
        return self.status == 'success'

    @property
    def health_color_class(self):
        """Tailwind classes for the health badge, by label."""
        return HEALTH_COLOR_CLASSES.get(self.health_label, DEFAULT_HEALTH_COLOR_CLASS)

    @property
    def health_text_class(self):
        """Tailwind text colour for the health score, by label."""
        return HEALTH_TEXT_CLASSES.get(self.health_label, DEFAULT_HEALTH_TEXT_CLASS)
