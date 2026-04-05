from django import forms

from .models import Account


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'initial_balance']
        labels = {
            'name': 'Nome',
            'account_type': 'Tipo de conta',
            'initial_balance': 'Saldo inicial',
        }
        widgets = {
            'initial_balance': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
