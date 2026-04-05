from django.conf import settings
from django.db import models


TRANSACTION_TYPE_CHOICES = [
    ('income', 'Entrada'),
    ('expense', 'Saída'),
]


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Usuário',
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Conta',
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Categoria',
    )
    description = models.CharField(max_length=200, verbose_name='Descrição')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor',
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name='Tipo',
    )
    date = models.DateField(verbose_name='Data')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'

    def __str__(self):
        return f'{self.description} - R$ {self.amount}'
