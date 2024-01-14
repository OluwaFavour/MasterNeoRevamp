from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from jobs.models import Job, JobType
from talents.models import Talent, Review, Experience, Skill


class CustomSerializer(serializers.Serializer):
    """
    Serializer for custom data.
    
    This serializer is used to serialize and deserialize custom data
    for talents, jobs, reviews, and experiences.
    """
    talents = serializers.CharField(max_length=200)
    jobs = serializers.CharField(max_length=200)
    reviews = serializers.CharField(max_length=200)
    experiences = serializers.CharField(max_length=200)


class JobOutSerializer(serializers.ModelSerializer):
    """
    Serializer for the Job model used for outputting job data.
    """

    job_types = serializers.StringRelatedField(many=True)
    class Meta:
        model = Job
        fields = [
            "id",
            "job_logo",
            "job_link",
            "job_title",
            "location",
            "time_added",
            "job_description",
            "job_types",
        ]

class JobInSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Job instance.

    This serializer defines the fields that can be included when creating a new Job instance.

    Fields:
    - id: The ID of the job.
    - job_logo: The logo of the job.
    - job_link: The link to the job.
    - job_title: The title of the job.
    - location: The location of the job.
    - job_description: The description of the job.
    """
    class Meta:
        model = Job
        fields = [
            "id",
            "job_logo",
            "job_link",
            "job_title",
            "location",
            "job_description",
        ]

class JobTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobType model.
    """
    class Meta:
        model = JobType
        fields = [
            "name",
        ]


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Skill model.
    """
    class Meta:
        model = Skill
        fields = [
            "name",
        ]


class TalentSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Talent model.

    This serializer is used to convert Talent model instances into JSON
    representation and vice versa. It defines the fields that should be
    included in the serialized output.

    Attributes:
        timezone (TimeZoneSerializerField): Serializer field for the timezone.
        skills (serializers.StringRelatedField): Serializer field for the skills.

    Meta:
        model (Talent): The model class that the serializer corresponds to.
        fields (list): The fields to be included in the serialized output.
    """

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
    """
    Serializer for the 'username' field of the Talent model.
    """
    class Meta:
        model = Talent
        fields = [
            "username",
        ]


class AboutMeSerializer(serializers.ModelSerializer):
    """
    Serializer for the 'about_me' field of the Talent model.
    """
    class Meta:
        model = Talent
        fields = [
            "about_me",
        ]


class SummarySerializer(serializers.ModelSerializer):
    """
    Serializer for the 'summary' field of the Talent model.
    """
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
    """
    Serializer for the Experience model.

    Serializes the Experience model fields into JSON format.
    """

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
    """
    Serializer class for Experience model to output data.
    """
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
