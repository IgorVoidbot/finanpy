from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.models import Account
from transactions.models import Transaction


class LandingView(TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_balance = Account.objects.filter(
            user=self.request.user
        ).aggregate(total=Sum('current_balance'))['total'] or 0

        today = date.today()
        month_start = today.replace(day=1)

        monthly_income = Transaction.objects.filter(
            user=self.request.user,
            transaction_type='income',
            date__gte=month_start,
            date__lte=today,
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_expense = Transaction.objects.filter(
            user=self.request.user,
            transaction_type='expense',
            date__gte=month_start,
            date__lte=today,
        ).aggregate(total=Sum('amount'))['total'] or 0

        monthly_balance = monthly_income - monthly_expense

        recent_transactions = Transaction.objects.filter(
            user=self.request.user
        ).select_related('account', 'category')[:5]

        expenses_by_category = (
            Transaction.objects.filter(
                user=self.request.user,
                transaction_type='expense',
                date__gte=month_start,
                date__lte=today,
            )
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        context.update({
            'total_balance': total_balance,
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'monthly_balance': monthly_balance,
            'recent_transactions': recent_transactions,
            'expenses_by_category': expenses_by_category,
        })

        return context
