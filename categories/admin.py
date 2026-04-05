from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'transaction_type', 'created_at']
    list_filter = ['transaction_type']
