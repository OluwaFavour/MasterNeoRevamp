import json
import requests
import os
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

# CONSTANTS
API_ENDPOINT = os.getenv("API_ENDPOINT")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


def get_language_from_locale(locale: str) -> str:
    # Path to locale.json: oauth2/locale.json
    file_path = "oauth2/locale.json"

    # Open locale.json and load the contents into a dictionary
    with open(file_path, "r", encoding="utf-8") as locale_file:
        locale_data = json.load(locale_file)

    # Get the language from the locale
    language = locale_data.get(locale).split(",")[0]
    return language


def exchange_code(code: str) -> dict | Response:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(
            f"{API_ENDPOINT}/oauth2/token",
            data=data,
            headers=headers,
            auth=(CLIENT_ID, CLIENT_SECRET),
        )
    except requests.exceptions.RequestException as e:
        return Response({"Error": e}, status=HTTP_400_BAD_REQUEST)
    else:
        credentials = response.json()
        return credentials


def get_access_token(credentials: dict) -> str:
    access_token = credentials.get("access_token")
    return access_token


def get_refresh_token(credentials: dict) -> str:
    refresh_token = credentials.get("refresh_token")
    return refresh_token


def refresh_credentials(refresh_token: str) -> dict | Response:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(
            f"{API_ENDPOINT}/oauth2/token",
            data=data,
            headers=headers,
            auth=(CLIENT_ID, CLIENT_SECRET),
        )
    except requests.exceptions.RequestException as e:
        return Response({"Error": e}, status=HTTP_400_BAD_REQUEST)
    else:
        credentials = response.json()
        return credentials


def revoke_access_token(access_token: str):
    data = {"token": access_token, "token_type_hint": "access_token"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    requests.post(
        f"{API_ENDPOINT}/oauth2/token/revoke",
        data=data,
        headers=headers,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )


def get_user(access_token: str) -> dict:
    try:
        response = requests.get(
            f"{API_ENDPOINT}/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    except requests.exceptions.RequestException as e:
        return Response({"Error": e}, status=HTTP_400_BAD_REQUEST)
    else:
        user = response.json()
        return user


def get_avatar_url(user: dict) -> str:
    avatar_hash = user.get("avatar")
    avatar_url = (
        f"https://cdn.discordapp.com/avatars/{user.get('id')}/{avatar_hash}.webp"
    )
    return avatar_url
