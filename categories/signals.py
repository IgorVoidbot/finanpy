from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User
from .models import Category


DEFAULT_CATEGORIES = {
    'income': ['Salário', 'Freelance', 'Investimentos', 'Outros'],
    'expense': [
        'Alimentação',
        'Transporte',
        'Moradia',
        'Lazer',
        'Saúde',
        'Educação',
        'Outros',
    ],
}


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if not created:
        return

    categories = []
    for transaction_type, names in DEFAULT_CATEGORIES.items():
        for name in names:
            categories.append(
                Category(
                    user=instance,
                    name=name,
                    transaction_type=transaction_type,
                )
            )

    Category.objects.bulk_create(categories)
