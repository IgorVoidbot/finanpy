from django.urls import path

from .views import ProfileUpdateView

app_name = 'profiles'

urlpatterns = [
    path('perfil/', ProfileUpdateView.as_view(), name='profile_edit'),
]
