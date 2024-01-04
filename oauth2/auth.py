from django.contrib.auth.backends import BaseBackend
from talents.models import Talent
from .utils import get_language_from_locale


class DiscordAuthenticationBackend(BaseBackend):
    # def __init__(self, client_id, client_secret):
    #     self.client_id = client_id
    #     self.client_secret = client_secret

    def authenticate(self, request, user: dict) -> Talent:
        try:
            talent = Talent.objects.get(id=user.get("id"))
        except Talent.DoesNotExist:
            print("User not found... Creating new user")
            talent = Talent.objects.create_talent(user)
        return talent
    
    def get_user(self, user_id):
        try:
            return Talent.objects.get(pk=user_id)
        except Talent.DoesNotExist:
            return None
