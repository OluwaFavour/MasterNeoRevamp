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

# CONSTANTS
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")


@login_required(login_url="oauth2/discord/login/")
def get_authenticated_user(request):
    return JsonResponse({"message": "You are authenticated"})


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

        if access_token is None:
            return Response({"error": "Failed to get access token"}, status=400)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
            }
        )


class RefreshTokenView(APIView):
    """
    API view for refreshing access token using a refresh token.
    """

    def post(self, request, format=None):
        """
        Handle POST requests for refreshing access token.

        Args:
            request (HttpRequest): The HTTP request object.
            format (str, optional): The format of the response. Defaults to None.

        Returns:
            Response: The HTTP response containing the new access token and its expiration time.
            If the refresh token is not provided, an error response is returned.
        """
        auth = DiscordAuthentication()
        refresh_token = request.data.get("refresh_token")
        if refresh_token is None:
            return Response({"error": "Refresh token not provided"}, status=400)
        new_access_token, expires_in = auth.refresh_token(refresh_token)
        return Response({"access_token": new_access_token, "expires_in": expires_in})


class RevokeTokenView(APIView):
    """
    API view for revoking an access token.
    """

    def post(self, request, format=None):
        """
        Handle POST requests to revoke an access token.

        Parameters:
        - request: The HTTP request object.
        - format: The format of the response data (default: None).

        Returns:
        - Response: The HTTP response object containing the result of the token revocation.
        """
        auth = DiscordAuthentication()
        access_token = request.data.get("access_token")
        if access_token is None:
            return Response({"error": "Access token not provided"}, status=400)
        is_revoked = auth.revoke_token(access_token)
        return Response({"is_revoked": is_revoked})
