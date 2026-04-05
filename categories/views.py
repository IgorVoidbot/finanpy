from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from categories.forms import CategoryForm
from categories.models import Category


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('categories:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        category = self.get_object()
        if category.transactions.exists():
            messages.error(
                self.request,
                'Não é possível excluir uma categoria com transações vinculadas.',
            )
            return redirect(self.success_url)
        messages.success(self.request, 'Categoria excluída com sucesso!')
        return super().form_valid(form)
