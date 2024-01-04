from django.urls import path
from .views import (
    discord_login,
    discord_login_redirect,
)
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("discord/login/", discord_login, name="discord-login"),
    path(
        "discord/login/redirect", discord_login_redirect, name="discord-login-redirect"
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
