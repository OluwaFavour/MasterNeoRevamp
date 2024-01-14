from drf_spectacular.extensions import OpenApiAuthenticationExtension


class DiscordAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Represents a Discord authentication scheme for OpenAPI.
    """

    target_class = (
        "oauth2.auth.DiscordAuthentication"  # Path to your DiscordAuthentication class
    )
    name = "discordAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
        }
