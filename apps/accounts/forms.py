from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
)
from django import forms
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.query_utils import Q
from .models import User


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]


class MyPasswordResetForm(PasswordResetForm):
    email = None
    username_or_email = forms.CharField(
        label="Username or Email",
        max_length=254,
    )

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):

        email = self.cleaned_data["username_or_email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        user = User.objects.get(Q(username__iexact=email) | Q(email__iexact=email))
        context = {
            "email": user.email,
            "domain": domain,
            "site_name": site_name,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "user": user,
            "token": token_generator.make_token(user),
            "protocol": "https" if use_https else "http",
            **(extra_email_context or {}),
        }
        self.send_mail(
            subject_template_name,
            email_template_name,
            context,
            from_email,
            user.email,
            html_email_template_name=html_email_template_name,
        )


class LogInForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Email",
        max_length=254,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]
