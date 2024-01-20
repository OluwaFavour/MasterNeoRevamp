import os
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from .auth import DiscordAuthentication, TwitterAuthentication
from api.openapi_extensions import DiscordAuthenticationScheme
from .utils import (
    generate_twitter_authorization_url,
    exchange_twitter_code,
    refresh_twitter_token,
    get_twitter_user,
)

# CONSTANTS
DISCORD_AUTHORIZATION_URL = os.getenv("DISCORD_AUTHORIZATION_URL")


def twitter_login(request):
    """
    Redirects the user to the Twitter authorization URL for login.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A redirect response to the Twitter authorization URL.
    """
    twitter_authorization_url, code_verifier = generate_twitter_authorization_url()
    request.session["code_verifier"] = code_verifier
    return redirect(twitter_authorization_url)


class TwitterRedirectView(APIView):
    """
    View for handling Twitter OAuth2 redirect.
    """

    authentication_classes = []

    def get(self, request, format=None) -> Response:
        """
        Handle GET requests to obtain access token from Twitter.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str, optional): The format of the response. Defaults to None.

        Returns:
            Response: The HTTP response containing the access token, refresh token, and expiration time.
                     If the code is not provided or access token retrieval fails, an error response is returned.
        """
        code = request.GET.get("code")
        if code is None:
            return Response({"error": "Code not provided"}, status=400)

        code_verifier = request.session.pop("code_verifier", None)
        auth = TwitterAuthentication()

        access_token, refresh_token, expires_in = auth.get_access_token(
            code, code_verifier
        )
        if access_token is None:
            return Response({"error": "Failed to get access token"}, status=400)
        auth.authenticate(request, token=access_token)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
            }
        )


class RefreshTwitterTokenView(APIView):
    """
    A view for refreshing Twitter access tokens.
    """

    authentication_classes = []

    def post(self, request, format=None):
        """
        Handle POST requests for refreshing access tokens.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str, optional): The format of the response. Defaults to None.

        Returns:
            Response: The HTTP response containing the new access token, refresh token, and expiration time.
        """
        auth = TwitterAuthentication()
        refresh_token = request.headers.get("Authorization")
        if not refresh_token:
            return Response({"error": "Authorization header is required"}, status=400)
        elif not refresh_token.startswith("Bearer "):
            return Response(
                {"error": "Bearer token is required in Authorization header"},
                status=401,
            )
        else:
            refresh_token = refresh_token.split(" ")[1]
        if refresh_token is None:
            return Response({"error": "Refresh token not provided"}, status=400)
        new_access_token, new_refresh_token, expires_in = auth.refresh_token(
            refresh_token
        )
        return Response(
            {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expires_in": expires_in,
            }
        )


class RevokeTwitterTokenView(APIView):
    """
    API view for revoking an access token.
    """

    authentication_classes = []

    def post(self, request, format=None):
        """
        Handle POST requests to revoke an access token.

        Parameters:
        - request: The HTTP request object.
        - format: The format of the response data (default: None).

        Returns:
        - Response: The HTTP response object containing the result of the token revocation.
        If the authorization header is missing or the access token is not provided, an error response is returned.
        """
        auth = TwitterAuthentication()
        access_token = request.headers.get("Authorization")
        if not access_token:
            return Response({"error": "Authorization header is required"}, status=400)
        elif not access_token.startswith("Bearer "):
            return Response(
                {"error": "Bearer token is required in Authorization header"},
                status=401,
            )
        access_token = access_token.split(" ")[1]
        if access_token is None:
            return Response({"error": "Access token not provided"}, status=400)
        is_revoked = auth.revoke_token(access_token)
        return Response({"is_revoked": is_revoked})


def discord_login_redirect(request):
    """
    Redirects the user to the Discord authorization URL.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A redirect response to the Discord authorization URL.
    """
    return redirect(DISCORD_AUTHORIZATION_URL)


class DiscordLoginView(APIView):
    """
    View for handling Discord OAuth2 redirect.
    """

    authentication_classes = []

    def get(self, request, format=None) -> Response:
        """
        Handle GET requests to obtain access token from Discord.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str, optional): The format of the response. Defaults to None.

        Returns:
            Response: The HTTP response containing the access token, refresh token, and expiration time.
                     If the code is not provided or access token retrieval fails, an error response is returned.
        """
        code = request.GET.get("code")
        if code is None:
            return Response({"error": "Code not provided"}, status=400)

        auth = DiscordAuthentication()
        # access_token, refresh_token, expires_in = auth.get_access_token(code)
        # if access_token is None:
        #     return Response({"error": "Failed to get access token"}, status=400)
        talent = auth.authenticate(request)

        return Response(
            {
                "id": talent.id,
                "username": talent.username,
                "avatar": talent.avatar,
            }
        )


class RefreshDiscordTokenView(APIView):
    """
    API view for refreshing access token using a refresh token.
    """

    authentication_classes = []

    def post(self, request, format=None):
        """
        Handle POST requests for refreshing access token.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str, optional): The format of the response. Defaults to None.

        Returns:
            Response: The HTTP response containing the new access token and its expiration time.
            If the authorization header is missing or the refresh token is not provided, an error response is returned.
        """
        auth = DiscordAuthentication()
        refresh_token = request.headers.get("Authorization")
        if not refresh_token:
            return Response({"error": "Authorization header is required"}, status=400)
        elif not refresh_token.startswith("Bearer "):
            return Response(
                {"error": "Bearer token is required in Authorization header"},
                status=401,
            )
        else:
            refresh_token = refresh_token.split(" ")[1]
        if refresh_token is None:
            return Response({"error": "Refresh token not provided"}, status=400)
        new_access_token, new_refresh_token, expires_in = auth.refresh_token(
            refresh_token
        )
        return Response(
            {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expires_in": expires_in,
            }
        )


class RevokeDiscordTokenView(APIView):
    """
    API view for revoking an access token.
    """

    authentication_classes = []

    def post(self, request, format=None):
        """
        Handle POST requests to revoke an access token.

        Parameters:
        - request: The HTTP request object.
        - format: The format of the response data (default: None).

        Returns:
        - Response: The HTTP response object containing the result of the token revocation.
        If the authorization header is missing or the access token is not provided, an error response is returned.
        """
        auth = DiscordAuthentication()
        access_token = request.headers.get("Authorization")
        if not access_token:
            return Response({"error": "Authorization header is required"}, status=400)
        elif not access_token.startswith("Bearer "):
            return Response(
                {"error": "Bearer token is required in Authorization header"},
                status=401,
            )
        access_token = access_token.split(" ")[1]
        if access_token is None:
            return Response({"error": "Access token not provided"}, status=400)
        is_revoked = auth.revoke_token(access_token)
        return Response({"is_revoked": is_revoked})
