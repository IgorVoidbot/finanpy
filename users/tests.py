import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestSignUp:
    def test_signup_page_loads(self, client):
        response = client.get(reverse('users:signup'))
        assert response.status_code == 200

    def test_signup_creates_user_and_logs_in(self, client):
        response = client.post(reverse('users:signup'), {
            'first_name': 'Novo',
            'last_name': 'Usuário',
            'email': 'novo@example.com',
            'password1': 'senha12345',
            'password2': 'senha12345',
        })

        assert response.status_code == 302
        assert response.url == reverse('dashboard')
        assert User.objects.filter(email='novo@example.com').exists()

        response = client.get(reverse('dashboard'))
        assert response.status_code == 200

    def test_signup_with_duplicate_email_fails(self, client, user):
        response = client.post(reverse('users:signup'), {
            'first_name': 'Outro',
            'last_name': 'Usuário',
            'email': user.email,
            'password1': 'senha12345',
            'password2': 'senha12345',
        })

        assert response.status_code == 200
        assert not User.objects.filter(email=user.email, first_name='Outro').exists()

    def test_signup_with_mismatched_passwords_fails(self, client):
        response = client.post(reverse('users:signup'), {
            'first_name': 'Novo',
            'last_name': 'Usuário',
            'email': 'senhadiferente@example.com',
            'password1': 'senha12345',
            'password2': 'outrasenha',
        })

        assert response.status_code == 200
        assert not User.objects.filter(email='senhadiferente@example.com').exists()


@pytest.mark.django_db
class TestLogin:
    def test_login_page_loads(self, client):
        response = client.get(reverse('users:login'))
        assert response.status_code == 200

    def test_login_with_valid_credentials_succeeds(self, client, user):
        response = client.post(reverse('users:login'), {
            'username': user.email,
            'password': 'testpass123',
        })

        assert response.status_code == 302
        assert response.url == reverse('dashboard')

    def test_login_with_invalid_email_fails(self, client, user):
        response = client.post(reverse('users:login'), {
            'username': 'naoexiste@example.com',
            'password': 'testpass123',
        })

        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated

    def test_login_with_wrong_password_fails(self, client, user):
        response = client.post(reverse('users:login'), {
            'username': user.email,
            'password': 'senhaerrada',
        })

        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
class TestLogout:
    def test_logout_redirects_to_landing(self, client, user):
        client.force_login(user)
        response = client.post(reverse('users:logout'))

        assert response.status_code == 302
        assert response.url == reverse('landing')

    def test_logout_ends_session(self, client, user):
        client.force_login(user)
        client.post(reverse('users:logout'))

        response = client.get(reverse('dashboard'))
        assert response.status_code == 302
        assert response.url.startswith(reverse('users:login'))
