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
    """
    Handles authentication using Discord OAuth2.

    This class provides methods for authenticating users, retrieving access tokens,
    refreshing tokens, and revoking tokens.
    """

    def authenticate(self, request) -> Talent:
        """
        Authenticates the request using the provided token and returns the corresponding Talent object.

        Args:
            request: The request object containing the token in the Authorization header.

        Returns:
            A tuple containing the authenticated Talent object and any potential error message.

        Raises:
            AuthenticationFailed: If the Authorization header is missing or if there is an error getting the user.
        """
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

    def get_access_token(self, code) -> tuple:
        """
        Retrieves the access token, refresh token, and expiration time for the given authorization code.

        Args:
            code (str): The authorization code.

        Returns:
            tuple: A tuple containing the access token, refresh token, and expiration time.
                    The access token is a string in the format "Bearer <access_token>".
                    The refresh token is a string in the format "Bearer <refresh_token>".
                    The expiration time is an integer representing the number of seconds until the access token expires.
        Raises:
            AuthenticationFailed: If an error occurs while retrieving the access token.
        """
        try:
            credentials = exchange_code(code)
            access_token = f"Bearer {get_access_token(credentials)}"
            refresh_token = f"Bearer {get_refresh_token(credentials)}"
            expires_in = credentials.get("expires_in")
            return access_token, refresh_token, expires_in
        except Exception as e:
            raise AuthenticationFailed(f"{e}")

    def refresh_token(self, refresh_token) -> tuple:
        """
        Refreshes the access token using the provided refresh token.

        Args:
            refresh_token (str): The refresh token to use for refreshing the access token.

        Returns:
            tuple: A tuple containing the new access token and its expiration time in seconds.

        Raises:
            AuthenticationFailed: If an error occurs while refreshing the access token.
        """
        try:
            credentials = refresh_credentials(refresh_token)
            new_access_token = f"Bearer {get_access_token(credentials)}"
            expires_in = credentials.get("expires_in")
            return new_access_token, expires_in
        except Exception as e:
            raise AuthenticationFailed(f"{e}")

    def revoke_token(self, access_token) -> bool:
        """
        Revoke the specified access token.

        Args:
            access_token (str): The access token to be revoked.

        Returns:
            bool: True if the access token was successfully revoked, False otherwise.

        Raises:
            AuthenticationFailed: If an error occurs while revoking the access token.
        """
        try:
            is_revoked = revoke_access_token(access_token)
            return is_revoked
        except Exception as e:
            raise AuthenticationFailed(f"{e}")
