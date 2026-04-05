from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import EmailAuthenticationForm, UserRegistrationForm


class SignUpView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('landing')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class UserLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'users/login.html'


class UserLogoutView(LogoutView):
    pass
