import datetime

import pytest
from django.urls import reverse

from .models import Category


@pytest.mark.django_db
class TestDefaultCategoriesSignal:
    def test_creates_eleven_default_categories(self, user):
        assert Category.objects.filter(user=user).count() == 11

    def test_default_income_categories(self, user):
        names = set(
            Category.objects.filter(user=user, transaction_type='income')
            .values_list('name', flat=True)
        )
        assert names == {'Salário', 'Freelance', 'Investimentos', 'Outros'}

    def test_default_expense_categories(self, user):
        names = set(
            Category.objects.filter(user=user, transaction_type='expense')
            .values_list('name', flat=True)
        )
        assert names == {
            'Alimentação', 'Transporte', 'Moradia', 'Lazer',
            'Saúde', 'Educação', 'Outros',
        }


@pytest.mark.django_db
class TestCategoryListView:
    def test_requires_login(self, client):
        response = client.get(reverse('categories:category_list'))
        assert response.status_code == 302

    def test_lists_only_own_categories(self, client, user, other_user):
        client.force_login(user)
        response = client.get(reverse('categories:category_list'))

        assert response.status_code == 200
        categories = response.context['categories']
        assert all(category.user == user for category in categories)
        assert categories.count() == Category.objects.filter(user=user).count()


@pytest.mark.django_db
class TestCategoryCreateView:
    def test_creates_category_for_logged_user(self, client, user):
        client.force_login(user)
        response = client.post(reverse('categories:category_create'), {
            'name': 'Categoria Nova',
            'transaction_type': 'income',
        })

        assert response.status_code == 302
        category = Category.objects.get(name='Categoria Nova')
        assert category.user == user

    def test_duplicate_name_and_type_for_same_user_fails(self, client, user):
        client.force_login(user)
        response = client.post(reverse('categories:category_create'), {
            'name': 'Salário',
            'transaction_type': 'income',
        })

        assert response.status_code == 200
        assert Category.objects.filter(
            user=user, name='Salário', transaction_type='income'
        ).count() == 1

    def test_same_name_allowed_for_different_users(self, client, user, other_user):
        client.force_login(user)
        response = client.post(reverse('categories:category_create'), {
            'name': 'Categoria Compartilhada',
            'transaction_type': 'income',
        })
        assert response.status_code == 302

        client.force_login(other_user)
        response = client.post(reverse('categories:category_create'), {
            'name': 'Categoria Compartilhada',
            'transaction_type': 'income',
        })
        assert response.status_code == 302

        assert Category.objects.filter(name='Categoria Compartilhada').count() == 2


@pytest.mark.django_db
class TestCategoryUpdateView:
    def test_updates_own_category(self, client, user, income_category):
        client.force_login(user)
        response = client.post(
            reverse('categories:category_update', args=[income_category.pk]),
            {'name': 'Nome Atualizado', 'transaction_type': 'income'},
        )

        assert response.status_code == 302
        income_category.refresh_from_db()
        assert income_category.name == 'Nome Atualizado'

    def test_cannot_update_other_users_category(self, client, other_user, income_category):
        client.force_login(other_user)
        response = client.post(
            reverse('categories:category_update', args=[income_category.pk]),
            {'name': 'Hackeado', 'transaction_type': 'income'},
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestCategoryDeleteView:
    def test_deletes_category_without_transactions(self, client, user, income_category):
        client.force_login(user)
        response = client.post(
            reverse('categories:category_delete', args=[income_category.pk])
        )

        assert response.status_code == 302
        assert not Category.objects.filter(pk=income_category.pk).exists()

    def test_blocks_deletion_of_category_with_transactions(
        self, client, user, account, expense_category
    ):
        from transactions.models import Transaction

        Transaction.objects.create(
            user=user,
            account=account,
            category=expense_category,
            description='Compra',
            amount='10.00',
            transaction_type='expense',
            date=datetime.date.today(),
        )

        client.force_login(user)
        response = client.post(
            reverse('categories:category_delete', args=[expense_category.pk])
        )

        assert response.status_code == 302
        assert Category.objects.filter(pk=expense_category.pk).exists()

    def test_cannot_delete_other_users_category(self, client, other_user, income_category):
        client.force_login(other_user)
        response = client.post(
            reverse('categories:category_delete', args=[income_category.pk])
        )
        assert response.status_code == 404
        assert Category.objects.filter(pk=income_category.pk).exists()
