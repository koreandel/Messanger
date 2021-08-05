from django.urls import reverse_lazy
from django.contrib.auth import views
from django.views.generic import TemplateView, CreateView
from .forms import RegistrationForm, LogInForm, MyPasswordResetForm


class MyLogoutView(views.LogoutView):
    template_name = "logout.html"


class RegistrationView(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "registration.html"


class SuccessLoginView(TemplateView):
    template_name = "success_login.html"


class MyLoginView(views.LoginView):
    form_class = LogInForm
    template_name = "login.html"


class MyPasswordResetView(views.PasswordResetView):
    form_class = MyPasswordResetForm
