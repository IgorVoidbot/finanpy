from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AccountForm
from .models import Account


class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


class AccountCreateView(LoginRequiredMixin, CreateView):
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Conta criada com sucesso.')
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('initial_balance', None)
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Conta atualizada com sucesso.')
        return super().form_valid(form)


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:account_list')

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Conta excluída com sucesso.')
        return super().form_valid(form)
