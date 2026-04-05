from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

from .models import User


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
        help_text='',
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        help_text='',
    )
    email = forms.EmailField(
        label='E-mail',
        help_text='',
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        help_text='A senha deve ter pelo menos 8 caracteres.',
    )
    password2 = forms.CharField(
        label='Confirmação de senha',
        widget=forms.PasswordInput,
        help_text='Digite a mesma senha para confirmação.',
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )
