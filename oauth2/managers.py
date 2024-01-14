from django.contrib.auth import models
from .utils import get_language_from_locale, get_avatar_url


class TalentOauth2Manager(models.UserManager):
    """
    Manager class for Talent model in OAuth2 authentication.
    """

    def create_talent(self, user: dict):
        """
        Create a Talent object based on the provided user dictionary.

        Args:
            user (dict): User dictionary containing user information.

        Returns:
            Talent: Created Talent object.
        """
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
