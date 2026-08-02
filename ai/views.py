from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import DetailView, ListView

from ai import services
from ai.models import AIAnalysis


class AnalysisListView(LoginRequiredMixin, ListView):
    model = AIAnalysis
    template_name = 'ai/analysis_list.html'
    context_object_name = 'analyses'
    paginate_by = 10

    def get_queryset(self):
        return AIAnalysis.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(services.analysis_panel_context(self.request.user))
        return context


class AnalysisDetailView(LoginRequiredMixin, DetailView):
    model = AIAnalysis
    template_name = 'ai/analysis_detail.html'
    context_object_name = 'analysis'

    def get_queryset(self):
        # Filtering by user turns another user's analysis into a 404.
        return AIAnalysis.objects.filter(user=self.request.user)


class GenerateAnalysisView(LoginRequiredMixin, View):
    """Runs an analysis on demand. POST only — a GET gets 405 from View."""

    def post(self, request, *args, **kwargs):
        redirect_url = self._redirect_url(request)

        if not services.is_enabled():
            messages.error(request, 'A análise inteligente está indisponível no momento.')
            return redirect(redirect_url)

        allowed, remaining = services.can_generate_analysis(request.user)
        if not allowed:
            messages.warning(
                request,
                'Você gerou uma análise há pouco. Tente novamente em '
                f'{remaining} minuto{"s" if remaining != 1 else ""}.',
            )
            return redirect(redirect_url)

        analysis = services.run_analysis_for_user(request.user)
        if analysis is None:
            messages.error(request, 'A análise inteligente está indisponível no momento.')
        elif analysis.is_success:
            messages.success(request, 'Nova análise gerada com sucesso.')
        else:
            messages.error(request, analysis.error_message)

        return redirect(redirect_url)

    def _redirect_url(self, request):
        """Goes back to where the button was clicked, defaulting to the dashboard."""
        next_url = request.POST.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return next_url
        return reverse('dashboard')
