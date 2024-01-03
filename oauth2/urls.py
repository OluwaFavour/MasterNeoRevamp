from django.urls import path
from .views import discord_login

urlpatterns = [
    path("discord/login/", discord_login, name="discord-login"),
]
