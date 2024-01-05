from django.urls import path
from .views import (
    discord_login,
    DiscordRedirectView,
    RefreshTokenView,
    RevokeTokenView,
)
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("discord/login/", discord_login, name="discord-login"),
    path(
        "discord/login/redirect",
        DiscordRedirectView.as_view(),
        name="discord-login-redirect",
    ),
    path("discord/refresh/", RefreshTokenView.as_view(), name="discord-refresh"),
    path("discord/revoke/", RevokeTokenView.as_view(), name="discord-revoke"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
