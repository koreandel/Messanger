from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("login/", views.MyLoginView.as_view(), name="login"),
    path("success_login/", views.SuccessLoginView.as_view(), name="success_login"),
    path("logout/", views.MyLogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        views.MyPasswordResetView.as_view(
            success_url=reverse_lazy("accounts:password_reset_done")
        ),
        name="password_reset",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_change.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="reset",
    ),
    path(
        "password_reset_complete",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
