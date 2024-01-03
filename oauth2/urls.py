from django.urls import path
from .views import discord_login, discord_login_redirect

urlpatterns = [
    path("discord/login/", discord_login, name="discord-login"),
    path(
        "discord/login/redirect", discord_login_redirect, name="discord-login-redirect"
    ),
]
