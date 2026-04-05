from django.conf import settings
from django.db import models


ACCOUNT_TYPE_CHOICES = [
    ('checking', 'Conta Corrente'),
    ('savings', 'Poupança'),
    ('wallet', 'Carteira'),
    ('investment', 'Investimento'),
]


class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
    )
    name = models.CharField(max_length=100)
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
    )
    initial_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    current_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.current_balance = self.initial_balance
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
