import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from accounts.models import Account
from categories.models import Category
from .models import Transaction


@pytest.mark.django_db
class TestTransactionModel:
    def test_str_representation(self, transaction):
        assert str(transaction) == f'{transaction.description} - R$ {transaction.amount}'


@pytest.mark.django_db
class TestBalanceUpdateSignal:
    def test_income_transaction_increases_balance(self, account, income_category):
        Transaction.objects.create(
            user=account.user,
            account=account,
            category=income_category,
            description='Salário',
            amount='2000.00',
            transaction_type='income',
            date=datetime.date.today(),
        )
        account.refresh_from_db()
        assert account.current_balance == Decimal('3000.00')

    def test_expense_transaction_decreases_balance(self, account, expense_category):
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
        assert account.current_balance == Decimal('700.00')

    def test_editing_amount_recalculates_balance(self, transaction):
        transaction.amount = Decimal('200.00')
        transaction.save()

        transaction.account.refresh_from_db()
        assert transaction.account.current_balance == Decimal('800.00')

    def test_deleting_transaction_reverts_balance(self, transaction):
        account = transaction.account
        transaction.delete()

        account.refresh_from_db()
        assert account.current_balance == Decimal('1000.00')


@pytest.mark.django_db
class TestTransactionForm:
    def test_rejects_zero_or_negative_amount(self, client, user, account, expense_category):
        client.force_login(user)
        response = client.post(reverse('transactions:transaction_create'), {
            'description': 'Inválida',
            'amount': '0',
            'date': datetime.date.today(),
            'transaction_type': 'expense',
            'account': account.pk,
            'category': expense_category.pk,
        })

        assert response.status_code == 200
        assert not Transaction.objects.filter(description='Inválida').exists()

    def test_rejects_category_type_mismatch(self, client, user, account, expense_category):
        client.force_login(user)
        response = client.post(reverse('transactions:transaction_create'), {
            'description': 'Tipo Errado',
            'amount': '50.00',
            'date': datetime.date.today(),
            'transaction_type': 'income',
            'account': account.pk,
            'category': expense_category.pk,
        })

        assert response.status_code == 200
        assert not Transaction.objects.filter(description='Tipo Errado').exists()


@pytest.mark.django_db
class TestTransactionListView:
    def test_requires_login(self, client):
        response = client.get(reverse('transactions:transaction_list'))
        assert response.status_code == 302

    def test_lists_only_own_transactions(self, client, user, other_user, transaction):
        other_account = Account.objects.create(
            user=other_user, name='Conta Outro', account_type='checking', initial_balance=Decimal('0'),
        )
        other_category = Category.objects.create(
            user=other_user, name='Categoria Outro', transaction_type='expense',
        )
        other_transaction = Transaction.objects.create(
            user=other_user,
            account=other_account,
            category=other_category,
            description='Transação de outro usuário',
            amount='10.00',
            transaction_type='expense',
            date=datetime.date.today(),
        )

        client.force_login(user)
        response = client.get(reverse('transactions:transaction_list'))

        transactions = list(response.context['transactions'])
        assert transaction in transactions
        assert other_transaction not in transactions

    def test_filter_by_transaction_type(self, client, user, account, income_category, expense_category):
        client.force_login(user)
        income_tx = Transaction.objects.create(
            user=user, account=account, category=income_category,
            description='Salário', amount='1000.00',
            transaction_type='income', date=datetime.date.today(),
        )
        expense_tx = Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Mercado', amount='100.00',
            transaction_type='expense', date=datetime.date.today(),
        )

        response = client.get(reverse('transactions:transaction_list'), {'transaction_type': 'income'})
        transactions = list(response.context['transactions'])

        assert income_tx in transactions
        assert expense_tx not in transactions

    def test_filter_by_date_range(self, client, user, account, expense_category):
        client.force_login(user)
        old_tx = Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Antiga', amount='10.00', transaction_type='expense',
            date=datetime.date(2020, 1, 1),
        )
        recent_tx = Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Recente', amount='10.00', transaction_type='expense',
            date=datetime.date.today(),
        )

        response = client.get(reverse('transactions:transaction_list'), {
            'date_from': (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
        })
        transactions = list(response.context['transactions'])

        assert recent_tx in transactions
        assert old_tx not in transactions

    def test_filter_by_account(self, client, user, account, expense_category):
        other_account = Account.objects.create(
            user=user, name='Outra Conta', account_type='savings', initial_balance=Decimal('0'),
        )
        client.force_login(user)
        tx_account_1 = Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Conta 1', amount='10.00', transaction_type='expense',
            date=datetime.date.today(),
        )
        tx_account_2 = Transaction.objects.create(
            user=user, account=other_account, category=expense_category,
            description='Conta 2', amount='10.00', transaction_type='expense',
            date=datetime.date.today(),
        )

        response = client.get(reverse('transactions:transaction_list'), {'account': account.pk})
        transactions = list(response.context['transactions'])

        assert tx_account_1 in transactions
        assert tx_account_2 not in transactions

    def test_pagination_is_twenty_per_page(self, client, user, account, expense_category):
        for i in range(25):
            Transaction.objects.create(
                user=user, account=account, category=expense_category,
                description=f'Transação {i}', amount='10.00', transaction_type='expense',
                date=datetime.date.today(),
            )

        client.force_login(user)
        response = client.get(reverse('transactions:transaction_list'))

        assert len(response.context['transactions']) == 20
        assert response.context['page_obj'].paginator.num_pages == 2


@pytest.mark.django_db
class TestTransactionCreateView:
    def test_creates_transaction_for_logged_user(self, client, user, account, expense_category):
        client.force_login(user)
        response = client.post(reverse('transactions:transaction_create'), {
            'description': 'Nova transação',
            'amount': '50.00',
            'date': datetime.date.today(),
            'transaction_type': 'expense',
            'account': account.pk,
            'category': expense_category.pk,
        })

        assert response.status_code == 302
        tx = Transaction.objects.get(description='Nova transação')
        assert tx.user == user

    def test_cannot_use_another_users_account(self, client, user, other_user, expense_category):
        other_account = Account.objects.create(
            user=other_user, name='Conta Outro', account_type='checking', initial_balance=Decimal('0'),
        )
        client.force_login(user)
        response = client.post(reverse('transactions:transaction_create'), {
            'description': 'Tentativa inválida',
            'amount': '50.00',
            'date': datetime.date.today(),
            'transaction_type': 'expense',
            'account': other_account.pk,
            'category': expense_category.pk,
        })

        assert response.status_code == 200
        assert not Transaction.objects.filter(description='Tentativa inválida').exists()


@pytest.mark.django_db
class TestTransactionUpdateView:
    def test_updates_own_transaction(self, client, user, transaction):
        client.force_login(user)
        response = client.post(
            reverse('transactions:transaction_update', args=[transaction.pk]),
            {
                'description': 'Atualizada',
                'amount': '99.00',
                'date': transaction.date,
                'transaction_type': transaction.transaction_type,
                'account': transaction.account.pk,
                'category': transaction.category.pk,
            },
        )

        assert response.status_code == 302
        transaction.refresh_from_db()
        assert transaction.description == 'Atualizada'
        assert transaction.amount == Decimal('99.00')

    def test_cannot_update_other_users_transaction(self, client, other_user, transaction):
        client.force_login(other_user)
        response = client.post(
            reverse('transactions:transaction_update', args=[transaction.pk]),
            {
                'description': 'Hackeada',
                'amount': '1.00',
                'date': transaction.date,
                'transaction_type': transaction.transaction_type,
                'account': transaction.account.pk,
                'category': transaction.category.pk,
            },
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestTransactionDeleteView:
    def test_deletes_own_transaction_and_reverts_balance(self, client, user, transaction):
        account = transaction.account
        client.force_login(user)
        response = client.post(reverse('transactions:transaction_delete', args=[transaction.pk]))

        assert response.status_code == 302
        assert not Transaction.objects.filter(pk=transaction.pk).exists()
        account.refresh_from_db()
        assert account.current_balance == Decimal('1000.00')

    def test_cannot_delete_other_users_transaction(self, client, other_user, transaction):
        client.force_login(other_user)
        response = client.post(reverse('transactions:transaction_delete', args=[transaction.pk]))

        assert response.status_code == 404
        assert Transaction.objects.filter(pk=transaction.pk).exists()
