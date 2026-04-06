from django import forms

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['description', 'amount', 'date', 'transaction_type', 'account', 'category']
        labels = {
            'description': 'Descrição',
            'amount': 'Valor',
            'date': 'Data',
            'transaction_type': 'Tipo',
            'account': 'Conta',
            'category': 'Categoria',
        }
        widgets = {
            'description': forms.TextInput(),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'transaction_type': forms.Select(),
            'account': forms.Select(),
            'category': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['account'].queryset = Account.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('O valor da transação deve ser maior que zero.')
        return amount

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')

        if transaction_type and category:
            if category.transaction_type != transaction_type:
                raise forms.ValidationError(
                    'A categoria selecionada não corresponde ao tipo da transação.'
                )

        return cleaned_data
