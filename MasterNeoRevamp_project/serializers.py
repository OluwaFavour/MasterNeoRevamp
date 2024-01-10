from rest_framework import serializers


class IndexCustomSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    api = serializers.CharField(max_length=200)
    discord_login = serializers.CharField(max_length=200)
