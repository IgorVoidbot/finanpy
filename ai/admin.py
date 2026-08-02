from django.contrib import admin

from ai.models import AIAnalysis


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'health_score', 'health_label', 'model_name', 'total_tokens', 'created_at']
    list_filter = ['status', 'health_label', 'model_name', 'created_at']
    search_fields = ['user__email', 'summary']
    date_hierarchy = 'created_at'
    # Analyses are produced by the agent — the admin is read-only on purpose
    readonly_fields = [
        'user',
        'status',
        'summary',
        'insights',
        'tips',
        'health_score',
        'health_label',
        'period_start',
        'period_end',
        'model_name',
        'prompt_tokens',
        'completion_tokens',
        'total_tokens',
        'duration_ms',
        'iterations',
        'error_message',
        'created_at',
        'updated_at',
    ]

    def has_add_permission(self, request):
        return False
