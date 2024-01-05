from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
@authentication_classes([])
def index(request, format=None):
    """
    API endpoint for the index page.
    """
    return Response(
        {
            "message": "Hello, World!, this is the index page.",
            "api": reverse("api-root", request=request, format=format),
            "discord_login": reverse("discord-login", request=request, format=format),
        }
    )
