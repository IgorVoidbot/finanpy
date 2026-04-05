from django import forms

from categories.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'transaction_type']
        labels = {
            'name': 'Nome',
            'transaction_type': 'Tipo',
        }
