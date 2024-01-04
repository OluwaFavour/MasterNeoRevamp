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
from .utils import exchange_code, get_access_token, get_user
from api.serializers import TalentSerializer, UsernameSerializer
from talents.models import Talent

# CONSTANTS
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")


@login_required(login_url="oauth2/discord/login/")
def get_authenticated_user(request):
    return JsonResponse({"message": "You are authenticated"})


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
        print(authenticated_user)
        login(request, authenticated_user)
        return Response(
            {
                "talent": TalentSerializer(authenticated_user).data,
            },
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(
            {"Error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST
        )

