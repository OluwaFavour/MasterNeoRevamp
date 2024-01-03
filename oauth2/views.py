import os
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import exchange_code, get_access_token, get_user

# CONSTANTS
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")

@api_view(["GET"])
def discord_login(request):
    return redirect(AUTHORIZATION_URL)


@api_view(["GET"])
def discord_login_redirect(request):
    code = request.GET.get("code")
    if code:
        credentials = exchange_code(code)
        access_token = get_access_token(credentials)
        user = get_user(access_token)
        authenticated_user = authenticate(request, user=user)
    return Response({"user": user})
