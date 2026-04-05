from django.contrib import admin

from transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'user', 'account', 'category', 'transaction_type', 'amount', 'date']
    list_filter = ['transaction_type', 'date', 'account', 'category']
    search_fields = ['description']
