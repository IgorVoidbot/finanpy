import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestLandingView:
    def test_renders_for_anonymous_visitor(self, client):
        response = client.get(reverse('landing'))

        assert response.status_code == 200

    def test_authenticated_user_goes_to_the_dashboard(self, client, user):
        client.force_login(user)
        response = client.get(reverse('landing'))

        assert response.status_code == 302
        assert response.url == reverse('dashboard')

    def test_calls_to_action_point_to_signup_and_login(self, client):
        body = client.get(reverse('landing')).content.decode()

        assert f'href="{reverse("users:signup")}"' in body
        assert f'href="{reverse("users:login")}"' in body

    def test_presents_the_ai_analysis(self, client):
        """A landing anuncia a análise inteligente — se a seção sumir, avisa."""
        body = client.get(reverse('landing')).content.decode()

        assert 'Análise Inteligente' in body
        assert 'Índice de saúde financeira' in body
        assert 'Gere sua análise' in body

    def test_does_not_link_to_the_ai_app(self, client):
        """A landing é pública e vive em develop antes da app `ai` existir lá.

        Um {% url 'ai:...' %} aqui quebraria a página inteira com
        NoReverseMatch — o link para as análises só faz sentido logado.
        """
        body = client.get(reverse('landing')).content.decode()

        assert 'href="/analises/' not in body
