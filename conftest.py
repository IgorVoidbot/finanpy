import datetime

import pytest
from django.contrib.auth import get_user_model

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password='testpass123',
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email='other@example.com',
        first_name='Other',
        last_name='User',
        password='testpass123',
    )


@pytest.fixture
def account(user):
    account = Account.objects.create(
        user=user,
        name='Conta Teste',
        account_type='checking',
        initial_balance='1000.00',
    )
    account.refresh_from_db()
    return account


@pytest.fixture
def income_category(user):
    return Category.objects.create(
        user=user,
        name='Categoria Entrada Teste',
        transaction_type='income',
    )


@pytest.fixture
def expense_category(user):
    return Category.objects.create(
        user=user,
        name='Categoria Saída Teste',
        transaction_type='expense',
    )


@pytest.fixture
def transaction(user, account, expense_category):
    return Transaction.objects.create(
        user=user,
        account=account,
        category=expense_category,
        description='Compra no mercado',
        amount='50.00',
        transaction_type='expense',
        date=datetime.date.today(),
    )
