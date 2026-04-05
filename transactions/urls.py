from django.urls import path

from transactions.views import (
    TransactionCreateView,
    TransactionDeleteView,
    TransactionListView,
    TransactionUpdateView,
)

app_name = 'transactions'

urlpatterns = [
    path('transacoes/', TransactionListView.as_view(), name='transaction_list'),
    path('transacoes/nova/', TransactionCreateView.as_view(), name='transaction_create'),
    path('transacoes/<int:pk>/editar/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('transacoes/<int:pk>/excluir/', TransactionDeleteView.as_view(), name='transaction_delete'),
]
