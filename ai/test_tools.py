"""Tests for the read-only tools handed to the finance agent."""

import pytest
from pydantic import ValidationError

from conftest import month_start
from ai.tools import build_tools


def tools_for(user):
    return {tool.name: tool for tool in build_tools(user)}


@pytest.mark.django_db
class TestToolValues:
    def test_financial_summary(self, user_with_history):
        result = tools_for(user_with_history)['get_financial_summary'].invoke({})

        assert result['currency'] == 'BRL'
        assert result['total_balance'] == 9000.0
        assert result['month_income'] == 5000.0
        assert result['month_expense'] == 1000.0
        assert result['month_balance'] == 4000.0
        assert result['accounts_count'] == 1
        assert result['transactions_count'] == 8
        assert result['first_transaction_date'] == month_start(1).isoformat()

    def test_accounts_overview(self, user_with_history):
        result = tools_for(user_with_history)['get_accounts_overview'].invoke({})

        assert result == [
            {
                'name': 'Conta Corrente',
                'type': 'Conta Corrente',
                'initial_balance': 1000.0,
                'current_balance': 9000.0,
            }
        ]

    def test_expenses_by_category_current_month(self, user_with_history):
        result = tools_for(user_with_history)['get_expenses_by_category'].invoke({'months': 1})

        assert result['total_expense'] == 1000.0
        assert result['period_start'] == month_start(0).isoformat()
        assert result['categories'] == [
            {'category': 'Alimentação', 'total': 800.0, 'percentage': 80.0, 'transactions': 2},
            {'category': 'Transporte', 'total': 200.0, 'percentage': 20.0, 'transactions': 1},
        ]

    def test_expenses_by_category_two_months(self, user_with_history):
        result = tools_for(user_with_history)['get_expenses_by_category'].invoke({'months': 2})

        assert result['total_expense'] == 3000.0
        assert result['period_start'] == month_start(1).isoformat()
        # Ordered from the biggest spender down
        assert [row['category'] for row in result['categories']] == [
            'Moradia',
            'Alimentação',
            'Transporte',
        ]
        assert [row['percentage'] for row in result['categories']] == [50.0, 43.3, 6.7]

    def test_income_by_category(self, user_with_history):
        result = tools_for(user_with_history)['get_income_by_category'].invoke({'months': 2})

        assert result['total_income'] == 11000.0
        assert result['categories'] == [
            {'category': 'Salário', 'total': 10000.0, 'percentage': 90.9, 'transactions': 2},
            {'category': 'Freelance', 'total': 1000.0, 'percentage': 9.1, 'transactions': 1},
        ]

    def test_monthly_totals(self, user_with_history):
        result = tools_for(user_with_history)['get_monthly_totals'].invoke({'months': 2})

        previous, current = result['months']
        assert previous == {
            'month': month_start(1).strftime('%Y-%m'),
            'income': 6000.0,
            'expense': 2000.0,
            'balance': 4000.0,
        }
        assert current == {
            'month': month_start(0).strftime('%Y-%m'),
            'income': 5000.0,
            'expense': 1000.0,
            'balance': 4000.0,
        }

    def test_monthly_totals_fills_months_without_transactions(self, user_with_history):
        result = tools_for(user_with_history)['get_monthly_totals'].invoke({'months': 6})

        assert len(result['months']) == 6
        # The four oldest months have no transaction at all
        assert all(month['income'] == 0.0 for month in result['months'][:4])
        assert all(month['expense'] == 0.0 for month in result['months'][:4])

    def test_recent_transactions(self, user_with_history):
        result = tools_for(user_with_history)['get_recent_transactions'].invoke({'limit': 3})

        assert len(result) == 3
        assert all(item['date'] == month_start(0).isoformat() for item in result)
        assert {item['type'] for item in result} <= {'income', 'expense'}
        assert all(item['amount'] > 0 for item in result)

    def test_largest_expenses(self, user_with_history):
        result = tools_for(user_with_history)['get_largest_expenses'].invoke(
            {'months': 2, 'limit': 2}
        )

        assert [expense['amount'] for expense in result['expenses']] == [1500.0, 500.0]
        assert result['expenses'][0]['description'] == 'Aluguel'
        assert result['expenses'][0]['category'] == 'Moradia'

    def test_no_data_returns_zeros_instead_of_failing(self, user):
        tools = tools_for(user)

        summary = tools['get_financial_summary'].invoke({})
        assert summary['total_balance'] == 0.0
        assert summary['transactions_count'] == 0
        assert summary['first_transaction_date'] is None

        expenses = tools['get_expenses_by_category'].invoke({'months': 6})
        assert expenses['total_expense'] == 0.0
        assert expenses['categories'] == []


@pytest.mark.django_db
class TestToolParameterLimits:
    def test_months_is_capped(self, user_with_history):
        result = tools_for(user_with_history)['get_expenses_by_category'].invoke({'months': 999})
        assert result['months'] == 24

    def test_months_has_a_floor(self, user_with_history):
        result = tools_for(user_with_history)['get_income_by_category'].invoke({'months': 0})
        assert result['months'] == 1

    def test_default_months_comes_from_the_setting(self, user_with_history, settings):
        settings.AI_ANALYSIS_MONTHS_WINDOW = 3
        tools = tools_for(user_with_history)

        assert len(tools['get_monthly_totals'].invoke({})['months']) == 3

    def test_non_integer_months_is_rejected_before_the_query(self, user_with_history):
        tools = tools_for(user_with_history)

        with pytest.raises(ValidationError):
            tools['get_expenses_by_category'].invoke({'months': 'muitos'})

    def test_limit_is_capped(self, user_with_history):
        result = tools_for(user_with_history)['get_largest_expenses'].invoke(
            {'months': 6, 'limit': 999}
        )
        # Only 5 expenses exist, but the cap must not raise or return everything blindly
        assert len(result['expenses']) == 5


@pytest.mark.django_db
class TestUserIsolation:
    """RF09.5 — a tool must never reach another user's data."""

    def test_no_tool_accepts_a_user_parameter(self, user):
        for tool in build_tools(user):
            argument_names = set(tool.args)
            assert 'user' not in argument_names
            assert 'user_id' not in argument_names
            assert argument_names <= {'months', 'limit'}

    def test_summary_ignores_another_users_data(self, user, other_user_with_history):
        result = tools_for(user)['get_financial_summary'].invoke({})

        assert result['total_balance'] == 0.0
        assert result['transactions_count'] == 0
        assert result['accounts_count'] == 0

    def test_accounts_of_another_user_are_invisible(
        self, user_with_history, other_user_with_history
    ):
        result = tools_for(user_with_history)['get_accounts_overview'].invoke({})

        assert [account['name'] for account in result] == ['Conta Corrente']

    def test_transactions_of_another_user_are_invisible(
        self, user_with_history, other_user_with_history
    ):
        tools = tools_for(user_with_history)

        assert len(tools['get_recent_transactions'].invoke({'limit': 50})) == 8
        assert tools['get_expenses_by_category'].invoke({'months': 6})['total_expense'] == 3000.0
        assert tools['get_income_by_category'].invoke({'months': 6})['total_income'] == 11000.0

    def test_each_user_sees_only_its_own_totals(
        self, user_with_history, other_user_with_history
    ):
        mine = tools_for(user_with_history)['get_financial_summary'].invoke({})
        theirs = tools_for(other_user_with_history)['get_accounts_overview'].invoke({})

        assert mine['accounts_count'] == 1
        assert [account['name'] for account in theirs] == ['Conta do Outro']
