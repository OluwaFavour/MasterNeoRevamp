import json
import requests
import os
from rest_framework.response import Response
from rest_framework import status

# CONSTANTS
API_ENDPOINT = os.getenv("API_ENDPOINT")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = (
    ("https://master-neo-revamp.onrender.com/oauth2/discord/login/redirect")
    if "RENDER" in os.environ
    else os.getenv("REDIRECT_URI")
)


def get_language_from_locale(locale: str) -> str:
    """
    Retrieves the language from the given locale.

    Args:
        locale (str): The locale string.

    Returns:
        str: The language extracted from the locale.

    Raises:
        FileNotFoundError: If the locale.json file is not found in the specified file path.
        AttributeError: If the locale is not found in the locale data.
    """
    # Path to locale.json: oauth2/locale.json
    file_path = "oauth2/locale.json"

    try:
        # Open locale.json and load the contents into a dictionary
        with open(file_path, "r", encoding="utf-8") as locale_file:
            locale_data = json.load(locale_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"locale.json not found in specified file path '{file_path}'"
        )
    else:
        try:
            # Get the language from the locale
            language = locale_data.get(locale).split(",")[0]
        except AttributeError as e:
            raise AttributeError(
                f"The locale '{locale}' was not found in the locale data."
            )
        else:
            return language


def exchange_code(code: str) -> dict:
    """
    Exchanges an authorization code for access token credentials.

    Args:
        code (str): The authorization code to exchange.

    Returns:
        dict: A dictionary containing the credentials.

    Raises:
        requests.exceptions.RequestException: If there is an error making the API request.
    """
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
        raise requests.exceptions.RequestException(
            "Error exchanging code for credentials from discord",
            response=response,
            request=e.request,
        )
    else:
        credentials = response.json()
        return credentials


def get_access_token(credentials: dict) -> str:
    """
    Retrieves the access token from the given credentials dictionary.

    Args:
        credentials (dict): A dictionary containing the credentials.

    Returns:
        str: The access token.

    """
    access_token = credentials.get("access_token")
    return access_token


def get_refresh_token(credentials: dict) -> str:
    """
    Retrieves the refresh token from the given credentials dictionary.

    Args:
        credentials (dict): A dictionary containing the credentials.

    Returns:
        str: The refresh token.

    """
    refresh_token = credentials.get("refresh_token")
    return refresh_token


def refresh_credentials(
    refresh_token: str,
) -> dict:
    """
    Refreshes the access token using the provided refresh token.

    Args:
        refresh_token (str): The refresh token used to obtain a new access token.

    Returns:
        dict: A dictionary containing the refreshed credentials.

    Raises:
        requests.exceptions.RequestException: If there is an error making the API request.
    """
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
        raise requests.exceptions.RequestException(
            "Error refreshing credentials from discord",
            response=response,
            request=e.request,
        )
    else:
        credentials = response.json()
        return credentials


def revoke_access_token(access_token: str) -> bool:
    """
    Revoke an access token.

    Args:
        access_token (str): The access token to be revoked.

    Returns:
        bool: True if the token was revoked successfully, False otherwise.
    """
    data = {"token": access_token, "token_type_hint": "access_token"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        f"{API_ENDPOINT}/oauth2/token/revoke",
        data=data,
        headers=headers,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )

    return response.status_code == 200


def get_user(authorization: str) -> dict:
    """
    Retrieves user information from the API using the provided authorization token.

    Args:
        authorization (str): The authorization token.

    Returns:
        dict: A dictionary containing the user information.

    Raises:
        requests.exceptions.RequestException: If there is an error making the API request.
    """
    try:
        response = requests.get(
            f"{API_ENDPOINT}/users/@me",
            headers={"Authorization": authorization},
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            "Error getting user from discord", response=response, request=e.request
        )
    else:
        user = response.json()
        if response.status_code != 200:
            print(user)
            raise requests.exceptions.RequestException(
                f"{user.get('message')}", response=response
            )
        else:
            return user


def get_avatar_url(user: dict) -> str:
    """
    Generate the URL for the avatar image of a user.

    Args:
        user (dict): A dictionary containing user information.

    Returns:
        str: The URL of the user's avatar image.

    Raises:
        ValueError: If the avatar hash is missing from the user data.
    """
    avatar_hash = user.get("avatar")
    if not avatar_hash:
        raise ValueError("Avatar hash is missing from user data")
    avatar_url = (
        f"https://cdn.discordapp.com/avatars/{user.get('id')}/{avatar_hash}.webp"
    )
    return avatar_url
