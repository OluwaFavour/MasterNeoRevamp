from django.contrib.auth.backends import BaseBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from oauth2.utils import (
    get_user,
    refresh_credentials,
    get_access_token,
    revoke_access_token,
    exchange_code,
    get_refresh_token,
)
from talents.models import Talent


class DiscordAuthentication(BaseAuthentication):
    def authenticate(self, request) -> Talent:
        token = request.headers.get("Authorization")

        if token is None:
            raise AuthenticationFailed("Authorization header is missing")

        try:
            user = get_user(token)
        except Exception as e:
            raise AuthenticationFailed(f"Error getting user: {e}")
        else:
            if user is None:
                return None
            try:
                talent = Talent.objects.get(id=user.get("id"))
            except Talent.DoesNotExist:
                print("User not found... Creating new user")
                talent = Talent.objects.create_talent(user)
            return (talent, None)

    def get_access_token(self, code):
        try:
            credentials = exchange_code(code)
            access_token = f"Bearer {get_access_token(credentials)}"
            refresh_token = f"Bearer {get_refresh_token(credentials)}"
            expires_in = credentials.get("expires_in")
            return access_token, refresh_token, expires_in
        except Exception as e:
            raise AuthenticationFailed(f"{e}")

    def refresh_token(self, refresh_token):
        try:
            credentials = refresh_credentials(refresh_token)
            new_access_token = f"Bearer {get_access_token(credentials)}"
            expires_in = credentials.get("expires_in")
            return new_access_token, expires_in
        except Exception as e:
            raise AuthenticationFailed(f"{e}")

    def revoke_token(self, access_token):
        try:
            is_revoked = revoke_access_token(access_token)
            return is_revoked
        except Exception as e:
            raise AuthenticationFailed(f"{e}")