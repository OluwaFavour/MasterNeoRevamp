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
from .auth import DiscordAuthentication
from api.openapi_extensions import DiscordAuthenticationScheme

# CONSTANTS
AUTHORIZATION_URL = (
    (
        "https://discord.com/api/oauth2/authorize?client_id=1192178284868423810&response_type=code&redirect_uri=https%3A%2F%2Fmaster-neo-revamp.onrender.com%2Foauth2%2Fdiscord%2Flogin%2Fredirect&scope=identify"
    )
    if "RENDER" in os.environ
    else os.getenv("AUTHORIZATION_URL")
)


def discord_login(request):
    """
    Redirects the user to the Discord authorization URL.

    Parameters:
    - request: The HTTP request object.

    Returns:
    - A redirect response to the Discord authorization URL.
    """
    return redirect(AUTHORIZATION_URL)


class DiscordRedirectView(APIView):
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
        access_token, refresh_token, expires_in = auth.get_access_token(code)
        auth.authenticate(request, token=access_token)

        if access_token is None:
            return Response({"error": "Failed to get access token"}, status=400)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
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
        new_access_token, expires_in = auth.refresh_token(refresh_token)
        return Response({"access_token": new_access_token, "expires_in": expires_in})


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
