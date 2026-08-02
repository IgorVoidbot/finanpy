"""Read-only tools used by the finance agent to inspect a single user's data.

Every tool is bound to one user by `build_tools()` through a closure. The
schema exposed to the model never carries a user identifier, so the model has
no way to ask for another user's data (RF09.5 in PRD.md). All database access
goes through the Django ORM with an explicit `user` filter — no free-form SQL
is ever handed to the model.

Monetary values are returned in Brazilian reais (BRL) as plain floats, and
dates as ISO 8601 strings, so results are always JSON serializable.
"""

import logging
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from langchain_core.tools import tool

from accounts.models import Account
from transactions.models import Transaction


logger = logging.getLogger(__name__)

# Caps applied to every parameter the model can influence
MAX_MONTHS = 24
DEFAULT_TRANSACTIONS = 20
MAX_TRANSACTIONS = 50
DEFAULT_LARGEST_EXPENSES = 10
MAX_LARGEST_EXPENSES = 20


def _clamp(value, default, minimum, maximum):
    """Coerces a model-provided number into a safe range."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(value, maximum))


def _money(value):
    """Converts a Decimal amount into a float with two decimal places."""
    if value is None:
        return 0.0
    return float(Decimal(value).quantize(Decimal('0.01')))


def _month_floor(reference, months_back):
    """Returns the first day of the month `months_back` months before."""
    total = reference.year * 12 + reference.month - 1 - months_back
    year, month = divmod(total, 12)
    return date(year, month + 1, 1)


def _month_key(value):
    return f'{value.year:04d}-{value.month:02d}'


def build_tools(user):
    """Builds the tool list bound to a single user.

    The user comes from the caller (the server), never from the model: no tool
    below declares a user parameter, which is what keeps one user's analysis
    from ever touching another user's data.
    """
    default_months = _clamp(
        getattr(settings, 'AI_ANALYSIS_MONTHS_WINDOW', 6), 6, 1, MAX_MONTHS
    )

    def user_transactions():
        return Transaction.objects.filter(user=user)

    def period_bounds(months):
        today = timezone.localdate()
        return _month_floor(today, months - 1), today

    @tool
    def get_financial_summary() -> dict:
        """Overall financial snapshot of the user: total balance across all
        accounts, income, expense and balance of the current month, how many
        accounts and transactions exist, and the date of the first transaction.

        Use this first to understand the general situation. Amounts are in BRL.
        """
        today = timezone.localdate()
        month_start = today.replace(day=1)

        accounts = Account.objects.filter(user=user)
        month_transactions = user_transactions().filter(
            date__gte=month_start, date__lte=today
        )
        income = month_transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        expense = month_transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        first_date = (
            user_transactions().order_by('date').values_list('date', flat=True).first()
        )

        return {
            'currency': 'BRL',
            'today': today.isoformat(),
            'current_month_start': month_start.isoformat(),
            'total_balance': _money(
                accounts.aggregate(total=Sum('current_balance'))['total']
            ),
            'month_income': _money(income),
            'month_expense': _money(expense),
            'month_balance': _money(income - expense),
            'accounts_count': accounts.count(),
            'transactions_count': user_transactions().count(),
            'first_transaction_date': first_date.isoformat() if first_date else None,
        }

    @tool
    def get_accounts_overview() -> list:
        """List of the user's bank accounts with name, type, initial balance
        and current balance, ordered by current balance (highest first).

        Amounts are in BRL. Useful to see how the money is distributed.
        """
        accounts = Account.objects.filter(user=user).order_by('-current_balance')
        return [
            {
                'name': account.name,
                'type': account.get_account_type_display(),
                'initial_balance': _money(account.initial_balance),
                'current_balance': _money(account.current_balance),
            }
            for account in accounts
        ]

    @tool
    def get_expenses_by_category(months: int = default_months) -> dict:
        """Expenses grouped by category over the last `months` months
        (1 to 24, counting the current month).

        Returns the analysed period, the total expense and, per category, the
        amount in BRL, the share of total expenses in percent and how many
        transactions it holds. Categories are ordered from highest to lowest.
        """
        months = _clamp(months, default_months, 1, MAX_MONTHS)
        start, end = period_bounds(months)

        rows = (
            user_transactions()
            .filter(transaction_type='expense', date__gte=start, date__lte=end)
            .values('category__name')
            .annotate(total=Sum('amount'), transactions=Count('id'))
            .order_by('-total')
        )
        total = sum((row['total'] for row in rows), Decimal('0'))

        return {
            'period_start': start.isoformat(),
            'period_end': end.isoformat(),
            'months': months,
            'total_expense': _money(total),
            'categories': [
                {
                    'category': row['category__name'],
                    'total': _money(row['total']),
                    'percentage': (
                        round(float(row['total'] / total * 100), 1) if total else 0.0
                    ),
                    'transactions': row['transactions'],
                }
                for row in rows
            ],
        }

    @tool
    def get_income_by_category(months: int = default_months) -> dict:
        """Income grouped by category over the last `months` months
        (1 to 24, counting the current month).

        Same shape as get_expenses_by_category, but for money coming in:
        period, total income and, per category, amount in BRL, share in percent
        and number of transactions.
        """
        months = _clamp(months, default_months, 1, MAX_MONTHS)
        start, end = period_bounds(months)

        rows = (
            user_transactions()
            .filter(transaction_type='income', date__gte=start, date__lte=end)
            .values('category__name')
            .annotate(total=Sum('amount'), transactions=Count('id'))
            .order_by('-total')
        )
        total = sum((row['total'] for row in rows), Decimal('0'))

        return {
            'period_start': start.isoformat(),
            'period_end': end.isoformat(),
            'months': months,
            'total_income': _money(total),
            'categories': [
                {
                    'category': row['category__name'],
                    'total': _money(row['total']),
                    'percentage': (
                        round(float(row['total'] / total * 100), 1) if total else 0.0
                    ),
                    'transactions': row['transactions'],
                }
                for row in rows
            ],
        }

    @tool
    def get_monthly_totals(months: int = default_months) -> dict:
        """Month-by-month series of income, expense and balance for the last
        `months` months (1 to 24, counting the current month).

        Months without any transaction are included with zeros, so the series
        is continuous and comparable. Use it to spot trends over time.
        """
        months = _clamp(months, default_months, 1, MAX_MONTHS)
        start, end = period_bounds(months)

        rows = (
            user_transactions()
            .filter(date__gte=start, date__lte=end)
            .annotate(month=TruncMonth('date'))
            .values('month', 'transaction_type')
            .annotate(total=Sum('amount'))
        )
        totals = {}
        for row in rows:
            key = _month_key(row['month'])
            bucket = totals.setdefault(key, {'income': Decimal('0'), 'expense': Decimal('0')})
            bucket[row['transaction_type']] += row['total']

        series = []
        for offset in range(months - 1, -1, -1):
            month_start = _month_floor(end, offset)
            bucket = totals.get(
                _month_key(month_start), {'income': Decimal('0'), 'expense': Decimal('0')}
            )
            series.append(
                {
                    'month': _month_key(month_start),
                    'income': _money(bucket['income']),
                    'expense': _money(bucket['expense']),
                    'balance': _money(bucket['income'] - bucket['expense']),
                }
            )

        return {
            'period_start': start.isoformat(),
            'period_end': end.isoformat(),
            'months': series,
        }

    @tool
    def get_recent_transactions(limit: int = DEFAULT_TRANSACTIONS) -> list:
        """The user's most recent transactions, newest first.

        `limit` goes from 1 to 50 (default 20). Each item has date,
        description, category, account, type ('income' or 'expense') and the
        amount in BRL as a positive number — the direction comes from the type.
        """
        limit = _clamp(limit, DEFAULT_TRANSACTIONS, 1, MAX_TRANSACTIONS)
        transactions = user_transactions().select_related('category', 'account')[:limit]

        return [
            {
                'date': transaction.date.isoformat(),
                'description': transaction.description,
                'category': transaction.category.name,
                'account': transaction.account.name,
                'type': transaction.transaction_type,
                'amount': _money(transaction.amount),
            }
            for transaction in transactions
        ]

    @tool
    def get_largest_expenses(
        months: int = default_months, limit: int = DEFAULT_LARGEST_EXPENSES
    ) -> dict:
        """The biggest single expenses over the last `months` months
        (1 to 24), ordered from largest to smallest.

        `limit` goes from 1 to 20 (default 10). Useful to identify one-off
        purchases that distort the month. Amounts are in BRL.
        """
        months = _clamp(months, default_months, 1, MAX_MONTHS)
        limit = _clamp(limit, DEFAULT_LARGEST_EXPENSES, 1, MAX_LARGEST_EXPENSES)
        start, end = period_bounds(months)

        transactions = (
            user_transactions()
            .filter(transaction_type='expense', date__gte=start, date__lte=end)
            .select_related('category', 'account')
            .order_by('-amount', '-date')[:limit]
        )

        return {
            'period_start': start.isoformat(),
            'period_end': end.isoformat(),
            'expenses': [
                {
                    'date': transaction.date.isoformat(),
                    'description': transaction.description,
                    'category': transaction.category.name,
                    'account': transaction.account.name,
                    'amount': _money(transaction.amount),
                }
                for transaction in transactions
            ],
        }

    return [
        get_financial_summary,
        get_accounts_overview,
        get_expenses_by_category,
        get_income_by_category,
        get_monthly_totals,
        get_recent_transactions,
        get_largest_expenses,
    ]
