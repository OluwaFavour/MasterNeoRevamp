from django.contrib.auth import models
from .utils import get_language_from_locale, get_avatar_url


class TalentOauth2Manager(models.UserManager):
    def create_talent(self, user: dict):
        language = get_language_from_locale(user.get("locale"))
        discord_tag = f"{user.get('username')}#{user.get('discriminator')}"
        avatar_url = get_avatar_url(user)
        talent = self.create(
            id=user.get("id"),
            avatar=avatar_url,
            global_name=user.get("global_name"),
            language=language,
            discord_profile=discord_tag,
        )
        return talent
