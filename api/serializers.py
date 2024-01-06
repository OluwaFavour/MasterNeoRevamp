from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from jobs.models import Job
from talents.models import Talent, Review, Experience


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "job_logo",
            "job_link",
            "company_name",
            "job_title",
            "location",
            "time_added",
            "job_description",
        ]


class TalentSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=True)

    class Meta:
        model = Talent
        fields = [
            "id",
            "username",
            "avatar",
            "global_name",
            "timezone",
            "language",
            "about_me",
            "summary",
            "profile_visits",
            "email",
            "discord_profile",
            "twitter_profile",
            "phone_number",
        ]


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talent
        fields = [
            "username",
        ]


class AboutMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talent
        fields = [
            "about_me",
        ]


class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Talent
        fields = [
            "summary",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "talent",
            "reviewer_name",
            "reviewer_organization",
            "review",
            "rating",
        ]


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            "id",
            "project_logo",
            "company_name",
            "role",
            "description",
            "start_date",
            "end_date",
            "currently_working",
            "discord_profile",
            "twitter_profile",
        ]

class ExperienceOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = [
            "id",
            "project_logo",
            "company_name",
            "role",
            "description",
            "start_date",
            "end_date",
            "currently_working",
            "verified",
            "discord_profile",
            "twitter_profile",
            "talent",
        ]
        depth = 1
