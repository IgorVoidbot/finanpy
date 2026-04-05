from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from transactions.models import Transaction


@receiver(post_save, sender=Transaction)
def update_balance_on_save(sender, instance, **kwargs):
    instance.account.update_account_balance()


@receiver(post_delete, sender=Transaction)
def update_balance_on_delete(sender, instance, **kwargs):
    instance.account.update_account_balance()
