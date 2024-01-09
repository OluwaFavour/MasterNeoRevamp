from oauth2.auth import DiscordAuthentication
from talents.models import Skill, Talent, Review, Experience
from jobs.models import Job, Company
from .serializers import (
    AboutMeSerializer,
    ExperienceOutputSerializer,
    JobSerializer,
    SummarySerializer,
    TalentSerializer,
    ExperienceSerializer,
    ReviewSerializer,
    UsernameSerializer,
    SkillSerializer,
)
from .permissions import IsTalentOrReadOnly, IsCompanyOrReadOnly
from django.conf import settings as djoser_settings
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.reverse import reverse


# Define an API root view to display available endpoints
@api_view(["GET"])
@authentication_classes([])
def api_root(request, format=None):
    """
    API root view.

    Returns a response with available API endpoints.

    Parameters:
    - request: The HTTP request object.
    - format: The requested format for the response.

    Returns:
    A Response object containing the available API endpoints.
    """
    return Response(
        {
            "talents": reverse("talent-list", request=request, format=format),
            "jobs": reverse("job-list", request=request, format=format),
            "reviews": reverse("review-list", request=request, format=format),
            "experiences": reverse("experience-list", request=request, format=format),
        }
    )


# Views for Job endpoints
class JobList(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating job instances.
    """

    queryset = Job.objects.all()
    serializer_class = JobSerializer
    authentication_classes = [djoser_settings.TOKEN_MODEL]

    def get_authenticators(self):
        if self.request is None or self.request.method == "GET":
            return []
        return super().get_authenticators()

    def perform_create(self, serializer):
        if not isinstance(self.request.user, Company):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save(company=self.request.user)


class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete individual job instances.

    This class-based view allows you to perform CRUD operations on individual job instances.
    It retrieves a single job instance, updates its data, or deletes it from the database.
    """

    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsCompanyOrReadOnly]
    authentication_classes = [djoser_settings.TOKEN_MODEL]
    
    def get_authenticators(self):
        if self.request is None or self.request.method == "GET":
            return []
        return super().get_authenticators()


# Views for Talent endpoints
class TalentList(generics.ListAPIView):
    """
    API endpoint for listing talent instances.

    Inherits from `generics.ListAPIView` and provides a list view for the `Talent` model.
    The `queryset` attribute is set to retrieve all instances of the `Talent` model.
    The `serializer_class` attribute is set to use the `TalentSerializer` for serialization.
    The `authentication_classes` attribute is set to an empty list, allowing unauthenticated access.

    Usage:
    - GET: Retrieve a list of talent instances.

    Example:
    To retrieve a list of talent instances, send a GET request to this endpoint.

    Note: Authentication is not required for accessing this endpoint.
    """

    queryset = Talent.objects.all()
    serializer_class = TalentSerializer


class TalentDetail(generics.RetrieveDestroyAPIView):
    """
    A view for retrieving, updating, and deleting individual talent instances.

    Attributes:
        queryset (QuerySet): The queryset of Talent objects.
        serializer_class (Serializer): The serializer class for Talent objects.

    Methods:
        get_authenticators: Returns the authenticators based on the request method.
        retrieve: Custom retrieve method to handle incrementing unique profile visits.
    """

    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    authentication_classes = [DiscordAuthentication]

    def get_authenticators(self):
        if self.request is None or self.request.method == "GET":
            return []
        return super().get_authenticators()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a talent instance and increment unique profile visits.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object.
        """
        instance = self.get_object()
        session_key = (
            request.session.session_key
            if hasattr(request.session, "session_key")
            else None
        )
        if session_key:
            instance.increment_unique_visits(session_key)
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not isinstance(request.user, Talent):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


@api_view(["PATCH"])
@authentication_classes([DiscordAuthentication])
def about_me(request, pk, format=None):
    """
    Update the 'about me' information of a talent.

    Args:
        request (Request): The HTTP request object.
        pk (int): The primary key of the talent.
        format (str, optional): The format of the response data. Defaults to None.

    Returns:
        Response: The HTTP response object.
    """
    if not isinstance(request.user, Talent):
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        talent = Talent.objects.get(pk=pk)
        if talent != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
    except Talent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AboutMeSerializer(talent, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@authentication_classes([DiscordAuthentication])
def summary(request, pk, format=None):
    """
    Update the summary of a talent.

    Args:
        request (Request): The HTTP request object.
        pk (int): The primary key of the talent to be updated.
        format (str, optional): The format of the response. Defaults to None.

    Returns:
        Response: The HTTP response containing the updated talent summary.
    """
    if not isinstance(request.user, Talent):
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        talent = Talent.objects.get(pk=pk)
        if talent != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
    except Talent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SummarySerializer(talent, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@authentication_classes([DiscordAuthentication])
def username(request, pk, format=None):
    """
    Update the username of a talent.

    Args:
        request (Request): The HTTP request object.
        pk (int): The primary key of the talent.
        format (str, optional): The format of the response data. Defaults to None.

    Returns:
        Response: The HTTP response object containing the updated username data or error messages.
    """
    if not isinstance(request.user, Talent):
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        talent = Talent.objects.get(pk=pk)
        if talent != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
    except Talent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UsernameSerializer(talent, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating skills of a talent.
    """

    serializer_class = SkillSerializer
    authentication_classes = [DiscordAuthentication]

    def get_authenticators(self):
        if self.request is None or self.request.method == "GET":
            return []
        return super().get_authenticators()

    def get_queryset(self):
        """
        Get the queryset of skills for the talent.

        Returns:
            QuerySet: The queryset of skills.

        Raises:
            NotFound: If the talent does not exist.
        """
        pk = self.kwargs.get("pk")
        try:
            talent = Talent.objects.get(pk=pk)
            if talent != self.request.user and self.request.method != "GET":
                raise PermissionDenied()
            return talent.skills
        except Talent.DoesNotExist:
            raise NotFound(detail="Talent not found.", code=404)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the skills of the talent.

        Returns:
            Response: The serialized skills data.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Update the skills of the talent.

        Returns:
            Response: The serialized updated skills data.

        Raises:
            Response: If the request data is invalid or exceeds the maximum limit.
        """
        if not isinstance(self.request.user, Talent):
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset()
        if len(request.data) > 5:
            return Response(
                {"detail": "You can only select a maximum of 5 skills."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = [{"name": name} for name in request.data.getlist("name")]
        queryset.clear()
        for skill_data in data:
            skill, _ = Skill.objects.get_or_create(name=skill_data["name"])
            queryset.add(skill)
        serializer = self.get_serializer(queryset.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Views for Experience endpoints
class ExperienceList(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating experience instances.
    """

    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    authentication_classes = [DiscordAuthentication]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ExperienceOutputSerializer
        return ExperienceSerializer

    def get_authenticators(self):
        if self.request is None or self.request.method == "GET":
            return []
        return super().get_authenticators()

    def perform_create(self, serializer):
        """
        Set the owner of the experience to the user making the request.
        """
        if not isinstance(self.request.user, Talent):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save(talent=self.request.user)


class ExperienceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting individual experience instances.
    """

    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [IsTalentOrReadOnly]
    authentication_classes = [DiscordAuthentication]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ExperienceOutputSerializer
        return ExperienceSerializer

    def get_authenticators(self):
        if self.request is None or self.request.method == "GET":
            return []
        return super().get_authenticators()


# Views for Review endpoints
class ReviewList(generics.ListCreateAPIView):
    # List and create review instances
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [djoser_settings.TOKEN_MODEL]

    def get_authenticators(self):
        if self.request is None or self.request.method == "GET":
            return []
        return super().get_authenticators()

    def perform_create(self, serializer):
        if not isinstance(self.request.user, Company):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save(reviewer_organization=self.request.user)


class ReviewDetail(generics.RetrieveAPIView):
    # Retrieve, update, and delete individual review instances
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = []
