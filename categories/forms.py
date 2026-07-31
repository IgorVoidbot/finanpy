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

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        transaction_type = cleaned_data.get('transaction_type')
        user_id = self.instance.user_id

        if user_id and name and transaction_type:
            queryset = Category.objects.filter(
                user_id=user_id, name=name, transaction_type=transaction_type,
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(
                    'Você já possui uma categoria com esse nome e tipo.'
                )

        return cleaned_data
