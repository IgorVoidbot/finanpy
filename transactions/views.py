from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.models import Account
from categories.models import Category
from transactions.forms import TransactionForm
from transactions.models import Transaction


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)
        params = self.request.GET

        date_from = params.get('date_from')
        if date_from:
            qs = qs.filter(date__gte=date_from)

        date_to = params.get('date_to')
        if date_to:
            qs = qs.filter(date__lte=date_to)

        transaction_type = params.get('transaction_type')
        if transaction_type:
            qs = qs.filter(transaction_type=transaction_type)

        account = params.get('account')
        if account:
            qs = qs.filter(account_id=account)

        category = params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = self.request.GET
        context['accounts'] = Account.objects.filter(user=self.request.user)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Transação criada com sucesso.')
        return super().form_valid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Transação atualizada com sucesso.')
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Transação excluída com sucesso.')
        return super().form_valid(form)
