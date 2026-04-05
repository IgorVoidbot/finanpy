from django.urls import path

from .views import AccountCreateView, AccountDeleteView, AccountListView, AccountUpdateView

app_name = 'accounts'

urlpatterns = [
    path('contas/', AccountListView.as_view(), name='account_list'),
    path('contas/nova/', AccountCreateView.as_view(), name='account_create'),
    path('contas/<int:pk>/editar/', AccountUpdateView.as_view(), name='account_update'),
    path('contas/<int:pk>/excluir/', AccountDeleteView.as_view(), name='account_delete'),
]
