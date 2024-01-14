from rest_framework import serializers
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer class for the Company model.
    """
    class Meta:
        model = Company