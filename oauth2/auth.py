from django.contrib.auth.backends import BaseBackend
from talents.models import Talent
from utils import get_language_from_locale


class DiscordAuthenticationBackend(BaseBackend):
    # def __init__(self, client_id, client_secret):
    #     self.client_id = client_id
    #     self.client_secret = client_secret

    def authenticate(self, request, user: dict) -> Talent:
        try:
            talent = Talent.objects.get(id=user.get("id"))
        except Talent.DoesNotExist:
            print("User not found... Creating new user")
            language = get_language_from_locale(user.get("locale"))
            discord_tag = f"{user.get('username')}#{user.get('discriminator')}"
            talent = Talent.objects.create(
                id=user.get("id"),
                avatar=user.get("avatar"),
                username=request.data.get("username"),
                global_name=user.get("global_name"),
                timezone=request.data.get("timezone"),
                language=language,
                discord_profile=discord_tag,
            )
            return talent
        return talent
