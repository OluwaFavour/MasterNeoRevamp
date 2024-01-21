from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from requests.exceptions import RequestException
from oauth2.utils import (
    exchange_twitter_code,
    get_twitter_user,
    get_user,
    refresh_credentials,
    get_access_token,
    refresh_twitter_token,
    revoke_access_token,
    exchange_code,
    get_refresh_token,
    revoke_twitter_token,
)
from talents.models import Talent


class TwitterAuthentication(BaseAuthentication):
    """
    Handles authentication using Twitter OAuth2 PKCE.

    This class provides methods for authenticating users, retrieving access tokens,
    refreshing tokens, and revoking tokens.
    """

    def authenticate(self, request, **kwargs) -> Talent:
        """
        Authenticates the user based on the provided token or Authorization header.

        Args:
            request: The HTTP request object.
            **kwargs: Additional keyword arguments.

        Returns:
            A tuple containing the authenticated Talent object and any potential error message.
        """
        token = kwargs.get("token")
        if token is None:
            token = request.headers.get("Authorization")
        elif token is None:
            raise AuthenticationFailed("Authorization header is missing")

        try:
            user = get_twitter_user(token)
        except RequestException as e:
            raise AuthenticationFailed(e)

        if user is None:
            return None

        try:
            talent = Talent.objects.get(twitter_id=user.get("id"))
            talent.signed_in_with = "Twitter"
            talent.save()
        except Talent.DoesNotExist:
            print("User not found... Creating new user")
            talent = Talent.objects.create_talent_twitter(user)
            talent.signed_in_with = "Twitter"
            talent.save()
        except Exception as e:
            raise AuthenticationFailed(f"Error getting user: {e}")
        return talent

    def get_access_token(self, code: str, code_verifier: str) -> tuple:
        """
        Retrieves the access token, refresh token, and expiration time for the given code and code verifier.

        Args:
            code (str): The authorization code.
            code_verifier (str): The code verifier.

        Returns:
            tuple: A tuple containing the access token, refresh token, and expiration time.
        """
        try:
            credentials = exchange_twitter_code(code, code_verifier)
            access_token = f"Bearer {get_access_token(credentials)}"
            refresh_token = f"Bearer {get_refresh_token(credentials)}"
            expires_in = credentials.get("expires_in")
            return access_token, refresh_token, expires_in
        except RequestException as e:
            raise AuthenticationFailed(e)

    def refresh_token(self, refresh_token: str) -> tuple:
        """
        Refreshes the access token using the provided refresh token.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            tuple: A tuple containing the new access token, new refresh token, and expires in value.
        """
        try:
            credentials = refresh_twitter_token(refresh_token)
            new_access_token = f"Bearer {get_access_token(credentials)}"
            new_refresh_token = f"Bearer {get_refresh_token(credentials)}"
            expires_in = credentials.get("expires_in")
            return new_access_token, new_refresh_token, expires_in
        except RequestException as e:
            raise AuthenticationFailed(e)

    def revoke_token(self, access_token: str) -> bool:
        """
        Revoke the specified access token.

        Args:
            access_token (str): The access token to be revoked.

        Returns:
            bool: True if the token was successfully revoked, False otherwise.

        Raises:
            AuthenticationFailed: If an error occurs while revoking the token.
        """
        try:
            is_revoked = revoke_twitter_token(access_token)
            return is_revoked
        except RequestException as e:
            raise AuthenticationFailed(e)


class DiscordAuthentication(BaseAuthentication):
    """
    Handles authentication using Discord OAuth2.

    This class provides methods for authenticating users, retrieving access tokens,
    refreshing tokens, and revoking tokens.
    """

    def authenticate(self, request, **kwargs) -> Talent:
        """
        Authenticates the request using the provided token and returns the corresponding Talent object.

        Args:
            request: The request object containing the token in the Authorization header.

        Returns:
            A tuple containing the authenticated Talent object and any potential error message.

        Raises:
            AuthenticationFailed: If the Authorization header is missing or if there is an error getting the user.
        """
        token = kwargs.get("token")
        if token is None:
            token = request.headers.get("Authorization")
        elif token is None:
            raise AuthenticationFailed("Authorization header is missing")

        try:
            user = get_user(token)
        except RequestException as e:
            raise AuthenticationFailed(e)

        if user is None:
            return None
        try:
            talent = Talent.objects.get(discord_id=user.get("id"))
            talent.signed_in_with = "Discord"
            talent.save()
        except Talent.DoesNotExist:
            print("User not found... Creating new user")
            talent = Talent.objects.create_talent_discord(user)
            talent.signed_in_with = "Discord"
            talent.save()
        except Exception as e:
            raise AuthenticationFailed(f"Error getting user: {e}")
        return talent

    def get_access_token(self, code: str) -> tuple:
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
        except RequestException as e:
            raise AuthenticationFailed(e)

    def refresh_token(self, refresh_token: str) -> tuple:
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
            new_refresh_token = f"Bearer {get_refresh_token(credentials)}"
            expires_in = credentials.get("expires_in")
            return new_access_token, new_refresh_token, expires_in
        except RequestException as e:
            raise AuthenticationFailed(e)

    def revoke_token(self, access_token: str) -> bool:
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
        except RequestException as e:
            raise AuthenticationFailed(e)


class DiscordOrTwitterAuthentication(BaseAuthentication):
    """
    Authenticates the user using either Discord or Twitter authentication methods.
    If Discord authentication fails, it falls back to Twitter authentication.
    """

    def authenticate(self, request):
        """
        Authenticates the user based on different authentication methods.

        Args:
            request: The request object containing the authentication credentials.

        Returns:
            The authenticated user if authentication is successful, None otherwise.

        Raises:
            AuthenticationFailed: If no valid authentication credentials are provided.
        """
        # Try DiscordAuthentication
        discord_auth = DiscordAuthentication()
        try:
            user = discord_auth.authenticate(request)
        except AuthenticationFailed:
            user = None
        if user is not None:
            return user

        # Try TwitterAuthentication
        twitter_auth = TwitterAuthentication()
        try:
            user = twitter_auth.authenticate(request)
        except AuthenticationFailed:
            user = None
        if user is not None:
            return user

        # If neither authentication method succeeds, raise AuthenticationFailed
        raise AuthenticationFailed("No valid authentication credentials provided.")
