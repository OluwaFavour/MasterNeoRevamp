from talents.models import Talent, Review, Experience
from jobs.models import Job
from .serializers import (
    AboutMeSerializer,
    JobSerializer,
    SummarySerializer,
    TalentSerializer,
    ExperienceSerializer,
    ReviewSerializer,
    UsernameSerializer,
)
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
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
    authentication_classes = []


class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete individual job instances.
    
    This class-based view allows you to perform CRUD operations on individual job instances.
    It retrieves a single job instance, updates its data, or deletes it from the database.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    authentication_classes = []


# Views for Talent endpoints
class TalentList(generics.ListAPIView):
    """
    API endpoint for listing and creating talent instances.

    Inherits from `generics.ListAPIView` and provides a list view for the `Talent` model.
    The `queryset` attribute is set to retrieve all instances of the `Talent` model.
    The `serializer_class` attribute is set to use the `TalentSerializer` for serialization.
    The `authentication_classes` attribute is set to an empty list, allowing unauthenticated access.

    Usage:
    - GET: Retrieve a list of talent instances.
    - POST: Create a new talent instance.

    Example:
    To retrieve a list of talent instances, send a GET request to this endpoint.

    To create a new talent instance, send a POST request to this endpoint with the required data.

    Note: Authentication is not required for accessing this endpoint.
    """
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    authentication_classes = []


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

    def get_authenticators(self):
        if self.request.method == "GET":
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


@api_view(["PATCH"])
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


# Views for Experience endpoints
class ExperienceList(generics.ListCreateAPIView):
    # List and create experience instances
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()


class ExperienceDetail(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete individual experience instances
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()


# Views for Review endpoints
class ReviewList(generics.ListCreateAPIView):
    # List and create review instances
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = []


class ReviewDetail(generics.RetrieveAPIView):
    # Retrieve, update, and delete individual review instances
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = []
