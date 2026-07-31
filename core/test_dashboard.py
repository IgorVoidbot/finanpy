import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


@pytest.mark.django_db
class TestDashboardView:
    def test_requires_login(self, client):
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302

    def test_total_balance_sums_all_own_accounts(self, client, user, account):
        Account.objects.create(
            user=user, name='Poupança', account_type='savings', initial_balance=Decimal('500.00'),
        )
        client.force_login(user)
        response = client.get(reverse('dashboard'))

        assert response.context['total_balance'] == Decimal('1500.00')

    def test_total_balance_ignores_other_users_accounts(self, client, user, other_user, account):
        Account.objects.create(
            user=other_user, name='Conta Outro', account_type='checking', initial_balance=Decimal('99999.00'),
        )
        client.force_login(user)
        response = client.get(reverse('dashboard'))

        assert response.context['total_balance'] == Decimal('1000.00')

    def test_monthly_income_and_expense_current_month_only(
        self, client, user, account, income_category, expense_category
    ):
        today = datetime.date.today()
        last_month = (today.replace(day=1) - datetime.timedelta(days=1))

        Transaction.objects.create(
            user=user, account=account, category=income_category,
            description='Salário', amount='3000.00', transaction_type='income', date=today,
        )
        Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Mercado', amount='400.00', transaction_type='expense', date=today,
        )
        Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Mês passado', amount='999.00', transaction_type='expense', date=last_month,
        )

        client.force_login(user)
        response = client.get(reverse('dashboard'))

        assert response.context['monthly_income'] == Decimal('3000.00')
        assert response.context['monthly_expense'] == Decimal('400.00')

    def test_monthly_balance_is_income_minus_expense(
        self, client, user, account, income_category, expense_category
    ):
        today = datetime.date.today()
        Transaction.objects.create(
            user=user, account=account, category=income_category,
            description='Salário', amount='3000.00', transaction_type='income', date=today,
        )
        Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Mercado', amount='400.00', transaction_type='expense', date=today,
        )

        client.force_login(user)
        response = client.get(reverse('dashboard'))

        assert response.context['monthly_balance'] == Decimal('2600.00')

    def test_dashboard_with_no_transactions_shows_zero(self, client, user, account):
        client.force_login(user)
        response = client.get(reverse('dashboard'))

        assert response.context['monthly_income'] == 0
        assert response.context['monthly_expense'] == 0
        assert response.context['monthly_balance'] == 0

    def test_recent_transactions_shows_at_most_five_most_recent(
        self, client, user, account, expense_category
    ):
        today = datetime.date.today()
        for i in range(7):
            Transaction.objects.create(
                user=user, account=account, category=expense_category,
                description=f'Transação {i}', amount='10.00', transaction_type='expense',
                date=today - datetime.timedelta(days=i),
            )

        client.force_login(user)
        response = client.get(reverse('dashboard'))

        recent = list(response.context['recent_transactions'])
        assert len(recent) == 5
        assert recent[0].description == 'Transação 0'

    def test_expenses_by_category_grouped_and_summed(
        self, client, user, account, expense_category
    ):
        other_expense_category = Category.objects.create(
            user=user, name='Outra Categoria Despesa', transaction_type='expense',
        )
        today = datetime.date.today()

        Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Compra 1', amount='100.00', transaction_type='expense', date=today,
        )
        Transaction.objects.create(
            user=user, account=account, category=expense_category,
            description='Compra 2', amount='50.00', transaction_type='expense', date=today,
        )
        Transaction.objects.create(
            user=user, account=account, category=other_expense_category,
            description='Compra 3', amount='30.00', transaction_type='expense', date=today,
        )

        client.force_login(user)
        response = client.get(reverse('dashboard'))

        totals = {
            row['category__name']: row['total']
            for row in response.context['expenses_by_category']
        }
        assert totals[expense_category.name] == Decimal('150.00')
        assert totals[other_expense_category.name] == Decimal('30.00')

    def test_dashboard_data_isolated_between_users(
        self, client, user, other_user, account, expense_category
    ):
        other_account = Account.objects.create(
            user=other_user, name='Conta Outro', account_type='checking', initial_balance=Decimal('50.00'),
        )
        other_category = Category.objects.create(
            user=other_user, name='Categoria Outro', transaction_type='expense',
        )
        Transaction.objects.create(
            user=other_user, account=other_account, category=other_category,
            description='Transação de outro usuário', amount='20.00',
            transaction_type='expense', date=datetime.date.today(),
        )

        client.force_login(user)
        response = client.get(reverse('dashboard'))

        descriptions = [t.description for t in response.context['recent_transactions']]
        assert 'Transação de outro usuário' not in descriptions
        assert response.context['total_balance'] == Decimal('1000.00')
