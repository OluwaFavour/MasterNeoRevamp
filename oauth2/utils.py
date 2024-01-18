import json
import requests
import base64
import random
import string
import hashlib
import os
import cloudinary.uploader
from urllib.parse import urlencode
from rest_framework.response import Response
from rest_framework import status


# CONSTANTS
DISCORD_API_ENDPOINT = os.getenv("DISCORD_API_ENDPOINT")
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

TWITTER_API_ENDPOINT = os.getenv("TWITTER_API_ENDPOINT")
TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI")


def upload_image(image_file) -> str:
    """
    Uploads an image to the image server.

    Args:
        image (str): The image to upload.

    Returns:
        str: The URL of the uploaded image.
    Raises:
        Exception: If there is an error uploading the image to the image server.
    """
    try:
        response = cloudinary.uploader.upload(
            image_file, folder="avatars", use_filename=True, unique_filename=True
        )
    except Exception as e:
        raise Exception("Error uploading image to image server")
    else:
        avatar_url = response.get("secure_url")
        return avatar_url


def generate_random_string(length: int) -> str:
    """
    Generates a random string of the specified length.

    Args:
        length (int): The length of the string to generate.

    Returns:
        str: The generated random string.
    """
    random_string = "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )
    return random_string


def generate_code_challenge(code_verifier: str) -> str:
    """
    Generate a code challenge from the provided code verifier.

    Args:
        code_verifier (str): The code verifier to generate the code challenge from.

    Returns:
        str: The generated code challenge.

    """
    hashed_verifier = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(hashed_verifier).rstrip(b"=").decode()
    return code_challenge


def generate_twitter_authorization_url() -> tuple[str, str]:
    """
    Generates the Twitter authorization URL for OAuth2 authentication.

    Returns:
        str: The Twitter authorization URL.
    """
    code_verifier = generate_random_string(64)
    state = generate_random_string(32)
    code_challenge = generate_code_challenge(code_verifier)

    twitter_authorization_url = (
        f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id={TWITTER_CLIENT_ID}"
        f"&redirect_uri={TWITTER_REDIRECT_URI}&scope=users.read%20tweet.read%20offline.access&state={state}"
        f"&code_challenge={code_challenge}&code_challenge_method=S256"
    )

    return twitter_authorization_url, code_verifier


def get_twitter_user(authorization: str) -> dict:
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
            f"{TWITTER_API_ENDPOINT}/users/me?user.fields=profile_image_url",
            headers={"Authorization": authorization},
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            "Error getting user from twitter", response=response, request=e.request
        )
    else:
        user = response.json()
        # if response.status_code != 200:
        #     print(user)
        #     raise requests.exceptions.RequestException(
        #         f"{user.get('error_description')}", response=response
        #     )
        # else:
        return user.get("data")


def get_twitter_request_headers() -> dict:
    """
    Returns the headers required for making a Twitter API request.

    The headers include the Authorization header with the client ID and client secret
    base64 encoded, and the Content-Type header set to 'application/x-www-form-urlencoded;charset=UTF-8'.

    Returns:
        dict: The headers for the Twitter API request.
    """
    # Base64 encode the client ID and client secret
    client_id_secret = f"{TWITTER_CLIENT_ID}:{TWITTER_CLIENT_SECRET}"
    client_id_secret_b64 = base64.b64encode(client_id_secret.encode("ascii")).decode(
        "utf-8"
    )

    headers = {
        "Authorization": f"Basic {client_id_secret_b64}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }

    return headers


def refresh_twitter_token(refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    headers = get_twitter_request_headers()

    try:
        response = requests.post(
            f"{TWITTER_API_ENDPOINT}/oauth2/token",
            data=urlencode(data),
            headers=headers,
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            "Error refreshing credentials from twitter",
            response=response,
            request=e.request,
        )
    else:
        credentials = response.json()
        return credentials


def revoke_twitter_token(access_token: str) -> bool:
    data = {"token": access_token}
    headers = get_twitter_request_headers()
    response = requests.post(
        f"{TWITTER_API_ENDPOINT}/oauth2/invalidate_token",
        data=urlencode(data),
        headers=headers,
    )

    return response.status_code == 200


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
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": "identify",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(
            f"{DISCORD_API_ENDPOINT}/oauth2/token",
            data=data,
            headers=headers,
            auth=(DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET),
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


def exchange_twitter_code(code: str, code_verifier: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": TWITTER_REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    headers = get_twitter_request_headers()

    try:
        response = requests.post(
            f"{TWITTER_API_ENDPOINT}/oauth2/token",
            data=urlencode(data),
            headers=headers,
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            "Error exchanging code for credentials from twitter",
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
            f"{DISCORD_API_ENDPOINT}/oauth2/token",
            data=data,
            headers=headers,
            auth=(DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET),
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
        f"{DISCORD_API_ENDPOINT}/oauth2/token/revoke",
        data=data,
        headers=headers,
        auth=(DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET),
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
            f"{DISCORD_API_ENDPOINT}/users/@me",
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
