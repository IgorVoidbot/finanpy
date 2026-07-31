import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestCrossUserAccessIsBlocked:
    """
    Garante que nenhum usuário logado consegue ler ou modificar
    contas, categorias ou transações de outro usuário via URL direta.
    """

    @pytest.mark.parametrize('url_name, object_fixture', [
        ('accounts:account_update', 'account'),
        ('accounts:account_delete', 'account'),
        ('categories:category_update', 'income_category'),
        ('categories:category_delete', 'income_category'),
        ('transactions:transaction_update', 'transaction'),
        ('transactions:transaction_delete', 'transaction'),
    ])
    def test_get_other_users_object_returns_404(
        self, client, other_user, url_name, object_fixture, request
    ):
        obj = request.getfixturevalue(object_fixture)
        client.force_login(other_user)

        response = client.get(reverse(url_name, args=[obj.pk]))

        assert response.status_code == 404

    @pytest.mark.parametrize('url_name, object_fixture', [
        ('accounts:account_update', 'account'),
        ('accounts:account_delete', 'account'),
        ('categories:category_update', 'income_category'),
        ('categories:category_delete', 'income_category'),
        ('transactions:transaction_update', 'transaction'),
        ('transactions:transaction_delete', 'transaction'),
    ])
    def test_post_other_users_object_returns_404_and_does_not_modify(
        self, client, other_user, url_name, object_fixture, request
    ):
        obj = request.getfixturevalue(object_fixture)
        model = type(obj)
        pk = obj.pk

        client.force_login(other_user)
        response = client.post(reverse(url_name, args=[pk]), {})

        assert response.status_code == 404
        assert model.objects.filter(pk=pk).exists()


@pytest.mark.django_db
class TestListViewsDoNotLeakOtherUsersData:
    def test_account_list_excludes_other_users_accounts(self, client, user, other_user, account):
        client.force_login(other_user)
        response = client.get(reverse('accounts:account_list'))
        assert account not in list(response.context['accounts'])

    def test_category_list_excludes_other_users_categories(
        self, client, user, other_user, income_category
    ):
        client.force_login(other_user)
        response = client.get(reverse('categories:category_list'))
        assert income_category not in list(response.context['categories'])

    def test_transaction_list_excludes_other_users_transactions(
        self, client, user, other_user, transaction
    ):
        client.force_login(other_user)
        response = client.get(reverse('transactions:transaction_list'))
        assert transaction not in list(response.context['transactions'])


@pytest.mark.django_db
class TestAllAuthenticatedViewsRequireLogin:
    @pytest.mark.parametrize('url_name', [
        'dashboard',
        'profiles:profile_edit',
        'accounts:account_list',
        'accounts:account_create',
        'categories:category_list',
        'categories:category_create',
        'transactions:transaction_list',
        'transactions:transaction_create',
    ])
    def test_anonymous_user_is_redirected_to_login(self, client, url_name):
        response = client.get(reverse(url_name))
        assert response.status_code == 302
        assert response.url.startswith(reverse('users:login'))
