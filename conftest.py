import datetime

import pytest
from django.contrib.auth import get_user_model

from accounts.models import Account
from ai.schemas import FinancialAnalysis
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


# --- AI analysis (app 'ai') ---------------------------------------------------


def month_start(offset=0):
    """First day of the month `offset` months before the current one."""
    today = datetime.date.today()
    total = today.year * 12 + today.month - 1 - offset
    year, month = divmod(total, 12)
    return datetime.date(year, month + 1, 1)


def build_transaction_history(user, account_name='Conta Corrente'):
    """Creates a deterministic history spread over the current and previous month.

    Uses the default categories created by the signal on the user. Totals the
    AI tools are expected to report:

        current month  — income 5000, expense 1000 (Alimentação 800, Transporte 200)
        previous month — income 6000, expense 2000 (Moradia 1500, Alimentação 500)
    """
    account = Account.objects.create(
        user=user,
        name=account_name,
        account_type='checking',
        initial_balance='1000.00',
    )
    # Reloads so initial_balance comes back as a Decimal — the balance signal
    # does arithmetic with it on every transaction saved below.
    account.refresh_from_db()

    def category(name, transaction_type):
        return Category.objects.get(user=user, name=name, transaction_type=transaction_type)

    entries = [
        (0, 'Salário', 'income', 'Salário do mês', '5000.00'),
        (0, 'Alimentação', 'expense', 'Mercado', '500.00'),
        (0, 'Alimentação', 'expense', 'Restaurante', '300.00'),
        (0, 'Transporte', 'expense', 'Combustível', '200.00'),
        (1, 'Salário', 'income', 'Salário do mês anterior', '5000.00'),
        (1, 'Freelance', 'income', 'Projeto extra', '1000.00'),
        (1, 'Moradia', 'expense', 'Aluguel', '1500.00'),
        (1, 'Alimentação', 'expense', 'Mercado', '500.00'),
    ]
    for offset, category_name, transaction_type, description, amount in entries:
        Transaction.objects.create(
            user=user,
            account=account,
            category=category(category_name, transaction_type),
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            date=month_start(offset),
        )

    account.refresh_from_db()
    return account


@pytest.fixture
def user_with_history(user):
    build_transaction_history(user)
    return user


@pytest.fixture
def other_user_with_history(other_user):
    build_transaction_history(other_user, account_name='Conta do Outro')
    return other_user


@pytest.fixture
def ai_enabled(settings):
    """Turns the agent on without any real credential."""
    settings.DEEPSEEK_API_KEY = 'sk-test-nao-e-uma-chave-real'
    settings.DEEPSEEK_MODEL = 'deepseek-chat'
    settings.AI_ANALYSIS_ENABLED = True
    settings.AI_ANALYSIS_MIN_INTERVAL_MINUTES = 15
    settings.AI_ANALYSIS_MONTHS_WINDOW = 6
    return settings


@pytest.fixture
def fake_analysis():
    """Fixed structured output returned by the agent double."""
    return FinancialAnalysis(
        summary='Você fechou o mês com sobra e o saldo segue crescendo.',
        insights=[
            'Alimentação consumiu 80% das saídas do mês.',
            'As entradas somaram R$ 5.000,00 no mês corrente.',
            'O saldo total das contas está positivo.',
        ],
        tips=[
            'Estabeleça um teto de R$ 600,00 para Alimentação.',
            'Reserve parte da sobra do mês antes de gastar.',
            'Registre as transações no mesmo dia para não perder o controle.',
        ],
        health_score=72,
        health_label='good',
        period_start=month_start(5),
        period_end=datetime.date.today(),
    )


class FakeAgent:
    """Stand-in for the LangChain agent — no test ever reaches the DeepSeek API."""

    def __init__(self, analysis, iterations=2, tokens_per_call=(100, 20)):
        self.analysis = analysis
        self.iterations = iterations
        self.tokens_per_call = tokens_per_call
        self.calls = []

    def invoke(self, payload, config=None):
        from langchain_core.messages import AIMessage, HumanMessage

        self.calls.append({'payload': payload, 'config': config})
        prompt_tokens, completion_tokens = self.tokens_per_call
        messages = [HumanMessage('mensagem do usuário')]
        for _ in range(self.iterations):
            messages.append(
                AIMessage(
                    '',
                    usage_metadata={
                        'input_tokens': prompt_tokens,
                        'output_tokens': completion_tokens,
                        'total_tokens': prompt_tokens + completion_tokens,
                    },
                )
            )
        return {'messages': messages, 'structured_response': self.analysis}


@pytest.fixture
def fake_agent(monkeypatch, fake_analysis):
    """Replaces the real agent in the service with the double above."""
    agent = FakeAgent(fake_analysis)
    monkeypatch.setattr('ai.services.build_finance_agent', lambda user: agent)
    return agent
