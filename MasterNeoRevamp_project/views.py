from rest_framework.generics import GenericAPIView
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import IndexCustomSerializer


class Index(GenericAPIView):
    """
    API endpoint for the index page.
    """

    serializer_class = IndexCustomSerializer

    def get(self, request, format=None):
        serializer = IndexCustomSerializer(
            data={
                "message": "Hello, World!, this is the index page.",
                "api": reverse("api-root", request=request, format=format),
                "discord_login": reverse(
                    "discord-login", request=request, format=format
                ),
            }
        )
        serializer.is_valid()
        return Response(serializer.data)
