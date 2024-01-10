from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from jobs.models import Job
from talents.models import Talent, Review, Experience, Skill


class CustomSerializer(serializers.Serializer):
    talents = serializers.CharField(max_length=200)
    jobs = serializers.CharField(max_length=200)
    reviews = serializers.CharField(max_length=200)
    experiences = serializers.CharField(max_length=200)


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name")

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


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "name",
        ]


class TalentSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=True)
    skills = serializers.StringRelatedField(many=True)

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
            "skills",  # Problem Outputs a list of skills pk instead of the skill name
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
    """
    Serializer class for the Review model.
    """

    talent_username = serializers.CharField(source="talent.username")

    class Meta:
        model = Review
        fields = [
            "id",
            "talent_username",
            "reviewer_name",
            "reviewer_position",
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
            "discord_link",
            "twitter_link",
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
            "discord_link",
            "twitter_link",
            "talent",
        ]
