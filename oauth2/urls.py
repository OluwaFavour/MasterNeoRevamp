from django.urls import path
from .views import (
    discord_login,
    DiscordRedirectView,
    RefreshDiscordTokenView,
    RevokeDiscordTokenView,
    twitter_login,
    TwitterRedirectView,
    RefreshTwitterTokenView,
    RevokeTwitterTokenView,
)
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("discord/login/", discord_login, name="discord-login"),
    path(
        "discord/login/redirect",
        DiscordRedirectView.as_view(),
        name="discord-login-redirect",
    ),
    path("discord/refresh/", RefreshDiscordTokenView.as_view(), name="discord-refresh"),
    path("discord/revoke/", RevokeDiscordTokenView.as_view(), name="discord-revoke"),
    path("twitter/login/", twitter_login, name="twitter-login"),
    path(
        "twitter/login/redirect",
        TwitterRedirectView.as_view(),
        name="twitter-login-redirect",
    ),
    path("twitter/refresh/", RefreshTwitterTokenView.as_view(), name="twitter-refresh"),
    path("twitter/revoke/", RevokeTwitterTokenView.as_view(), name="twitter-revoke"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
