from rest_framework.decorators import api_view
from django.shortcuts import redirect


authorization_url = "https://discord.com/api/oauth2/authorize?client_id=1192178284868423810&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fdiscord%2Flogin%2Fredirect&scope=identify"


@api_view(["GET"])
def discord_login(request):
    return redirect(authorization_url)
