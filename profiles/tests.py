import pytest
from django.urls import reverse

from .models import Profile


@pytest.mark.django_db
class TestProfileSignal:
    def test_profile_created_automatically_on_user_creation(self, user):
        assert Profile.objects.filter(user=user).exists()

    def test_profile_display_name_defaults_to_first_name(self, user):
        assert user.profile.display_name == user.first_name


@pytest.mark.django_db
class TestProfileUpdateView:
    def test_requires_login(self, client):
        response = client.get(reverse('profiles:profile_edit'))
        assert response.status_code == 302
        assert response.url.startswith(reverse('users:login'))

    def test_page_loads_with_prefilled_data(self, client, user):
        client.force_login(user)
        response = client.get(reverse('profiles:profile_edit'))

        assert response.status_code == 200
        assert response.context['user_form'].instance == user
        assert response.context['profile_form'].instance == user.profile

    def test_page_loads_when_profile_missing(self, client, user):
        Profile.objects.filter(user=user).delete()
        client.force_login(user)

        response = client.get(reverse('profiles:profile_edit'))

        assert response.status_code == 200
        assert Profile.objects.filter(user=user).exists()

    def test_updates_when_profile_missing(self, client, user):
        Profile.objects.filter(user=user).delete()
        client.force_login(user)

        response = client.post(reverse('profiles:profile_edit'), {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'display_name': 'Perfil Recriado',
        })

        assert response.status_code == 302
        profile = Profile.objects.get(user=user)
        assert profile.display_name == 'Perfil Recriado'

    def test_updates_user_and_profile_fields(self, client, user):
        client.force_login(user)
        response = client.post(reverse('profiles:profile_edit'), {
            'first_name': 'Atualizado',
            'last_name': user.last_name,
            'email': user.email,
            'display_name': 'Apelido Novo',
        })

        assert response.status_code == 302

        user.refresh_from_db()
        user.profile.refresh_from_db()
        assert user.first_name == 'Atualizado'
        assert user.profile.display_name == 'Apelido Novo'

    def test_update_with_duplicate_email_fails(self, client, user, other_user):
        client.force_login(user)
        response = client.post(reverse('profiles:profile_edit'), {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': other_user.email,
            'display_name': user.profile.display_name,
        })

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email != other_user.email

    def test_only_updates_own_profile(self, client, user, other_user):
        client.force_login(user)
        client.post(reverse('profiles:profile_edit'), {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'display_name': 'Só Meu',
        })

        other_user.profile.refresh_from_db()
        assert other_user.profile.display_name != 'Só Meu'
