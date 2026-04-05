from django.conf import settings
from django.db import models


TRANSACTION_TYPE_CHOICES = [
    ('income', 'Entrada'),
    ('expense', 'Saída'),
]


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
    )
    name = models.CharField(max_length=50)
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name', 'transaction_type']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
