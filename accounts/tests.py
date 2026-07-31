from decimal import Decimal

import pytest
from django.urls import reverse

from .models import Account


@pytest.mark.django_db
class TestAccountModel:
    def test_current_balance_equals_initial_balance_on_creation(self, user):
        account = Account.objects.create(
            user=user,
            name='Conta Nova',
            account_type='checking',
            initial_balance='500.00',
        )
        account.refresh_from_db()
        assert account.current_balance == Decimal('500.00')

    def test_current_balance_not_reset_on_update(self, account):
        account.current_balance = Decimal('999.00')
        account.save()
        account.refresh_from_db()
        assert account.current_balance == Decimal('999.00')

    def test_update_account_balance_recalculates_from_transactions(
        self, account, income_category, expense_category
    ):
        from transactions.models import Transaction
        import datetime

        Transaction.objects.create(
            user=account.user,
            account=account,
            category=income_category,
            description='Salário',
            amount='2000.00',
            transaction_type='income',
            date=datetime.date.today(),
        )
        Transaction.objects.create(
            user=account.user,
            account=account,
            category=expense_category,
            description='Mercado',
            amount='300.00',
            transaction_type='expense',
            date=datetime.date.today(),
        )

        account.refresh_from_db()
        assert account.current_balance == Decimal('1000.00') + Decimal('2000.00') - Decimal('300.00')


@pytest.mark.django_db
class TestAccountListView:
    def test_requires_login(self, client):
        response = client.get(reverse('accounts:account_list'))
        assert response.status_code == 302

    def test_lists_only_own_accounts(self, client, user, other_user, account):
        other_account = Account.objects.create(
            user=other_user,
            name='Conta Outro',
            account_type='savings',
            initial_balance='100.00',
        )

        client.force_login(user)
        response = client.get(reverse('accounts:account_list'))

        assert response.status_code == 200
        accounts = list(response.context['accounts'])
        assert account in accounts
        assert other_account not in accounts


@pytest.mark.django_db
class TestAccountCreateView:
    def test_creates_account_for_logged_user(self, client, user):
        client.force_login(user)
        response = client.post(reverse('accounts:account_create'), {
            'name': 'Carteira',
            'account_type': 'wallet',
            'initial_balance': '150.00',
        })

        assert response.status_code == 302
        account = Account.objects.get(name='Carteira')
        assert account.user == user
        assert account.current_balance == Decimal('150.00')


@pytest.mark.django_db
class TestAccountUpdateView:
    def test_updates_own_account(self, client, user, account):
        client.force_login(user)
        response = client.post(
            reverse('accounts:account_update', args=[account.pk]),
            {'name': 'Nome Atualizado', 'account_type': 'savings'},
        )

        assert response.status_code == 302
        account.refresh_from_db()
        assert account.name == 'Nome Atualizado'
        assert account.account_type == 'savings'

    def test_does_not_allow_editing_initial_balance(self, client, user, account):
        client.force_login(user)
        original_initial_balance = account.initial_balance

        response = client.post(
            reverse('accounts:account_update', args=[account.pk]),
            {
                'name': account.name,
                'account_type': account.account_type,
                'initial_balance': '99999.00',
            },
        )

        assert response.status_code == 302
        account.refresh_from_db()
        assert account.initial_balance == original_initial_balance

    def test_cannot_update_other_users_account(self, client, other_user, account):
        client.force_login(other_user)
        response = client.post(
            reverse('accounts:account_update', args=[account.pk]),
            {'name': 'Hackeado', 'account_type': 'savings'},
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestAccountDeleteView:
    def test_deletes_own_account(self, client, user, account):
        client.force_login(user)
        response = client.post(reverse('accounts:account_delete', args=[account.pk]))

        assert response.status_code == 302
        assert not Account.objects.filter(pk=account.pk).exists()

    def test_cannot_delete_other_users_account(self, client, other_user, account):
        client.force_login(other_user)
        response = client.post(reverse('accounts:account_delete', args=[account.pk]))

        assert response.status_code == 404
        assert Account.objects.filter(pk=account.pk).exists()
