from django.db.models import Q, Avg
from oauth2.auth import DiscordAuthentication
from .openapi_extensions import DiscordAuthenticationScheme
from talents.models import Skill, Talent, Review, Experience
from jobs.models import Job, Company, JobType
from .serializers import (
    AboutMeSerializer,
    ExperienceOutputSerializer,
    JobInSerializer,
    JobOutSerializer,
    SummarySerializer,
    TalentSerializer,
    ExperienceSerializer,
    ReviewSerializer,
    UsernameSerializer,
    SkillSerializer,
    CustomSerializer,
    JobTypeSerializer,
)
from .permissions import IsTalentOrReadOnly, IsCompanyOrReadOnly
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly


# Define an API root view to display available endpoints
class DefaultPagination(PageNumberPagination):
    """
    Default pagination class for API views.

    Attributes:
        page_size (int): The number of items to include on each page.
        page_size_query_param (str): The query parameter to control the page size.
        max_page_size (int): The maximum allowed page size.
    """
    page_size = 300
    page_size_query_param = "page_size"
    max_page_size = 1000


class APIRoot(generics.GenericAPIView):
    """
    API root view.

    Returns a response with available API endpoints.
    """

    serializer_class = CustomSerializer

    def get(self, request, format=None):
        """
        Handle GET requests.

        Parameters:
        - request: The HTTP request object.
        - format: The requested format for the response.

        Returns:
        A Response object containing the available API endpoints.
        """
        serializer = CustomSerializer(
            data={
                "talents": reverse("talent-list", request=request, format=format),
                "jobs": reverse("job-list", request=request, format=format),
                "reviews": reverse("review-list", request=request, format=format),
                "experiences": reverse(
                    "experience-list", request=request, format=format
                ),
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


# Views for Job endpoints
class JobList(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating job instances.

    Inherits from generics.ListCreateAPIView and provides functionality for listing and creating job instances.
    """

    queryset = Job.objects.all()
    serializer_class = JobInSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == "GET":
            return JobOutSerializer
        return JobInSerializer

    def get_queryset(self):
        """
        Returns the queryset of Job objects based on the provided query parameters.

        If job_types are provided in the query parameters, the queryset is filtered
        to include only jobs with matching job types.

        Returns:
            queryset (QuerySet): The filtered queryset of Job objects.
        """
        queryset = Job.objects.all()

        # Filter by job types if provided in query parameters
        job_types = self.request.query_params.getlist("job_types")
        if job_types:
            query_condition = Q()
            for job_type in job_types:
                query_condition |= Q(job_types__name__iexact=job_type)
            queryset = queryset.filter(query_condition)

        return queryset

    def perform_create(self, serializer):
        """
        Perform custom creation logic for the view.

        This method is called when creating a new object using the view.
        It checks if the request user is an instance of the Company model.
        If not, it returns a 403 Forbidden response.
        Otherwise, it saves the object with the company set to the request user.

        Args:
            serializer: The serializer instance used for object creation.

        Returns:
            None
        """
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
    serializer_class = JobInSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCompanyOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return JobOutSerializer
        return JobInSerializer


class JobTypeView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating job types for a job.

    Inherits:
        generics.RetrieveUpdateAPIView

    Attributes:
        authentication_classes (list): List of authentication classes for the view.
        permission_classes (list): List of permission classes for the view.
        serializer_class: Serializer class for the view.

    Methods:
        get_queryset: Get the queryset of job types for the job.
        get: Retrieve the job types of the job.
        put: Update the job types of the job.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = JobTypeSerializer

    def get_queryset(self):
        """
        Get the queryset of job types for the job.

        Returns:
            QuerySet: The queryset of job types.

        Raises:
            NotFound: If the job does not exist.
        """
        pk = self.kwargs.get("pk")
        try:
            job = Job.objects.get(pk=pk)
            if job.company != self.request.user and self.request.method != "GET":
                raise PermissionDenied()
            return job.job_types
        except Job.DoesNotExist:
            raise NotFound(detail="Job not found.", code=404)

    def get(self, request, *args, **kwargs):
        """
        Retrieve the job types of the job.

        Returns:
            Response: The serialized job types data.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Update the job types of the job.

        This method updates the job types associated with a job. It receives a list of job type names in the request data
        and updates the job's job types accordingly. If the request data is invalid, it raises a Response with an appropriate
        status code.

        Returns:
            Response: The serialized updated job types data.

        Raises:
            Response: If the request data is invalid.
        """
        if not isinstance(self.request.user, Company):
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset()
        data = [{"name": name} for name in request.data.getlist("name")]
        queryset.clear()
        for job_type_data in data:
            job_type, _ = JobType.objects.get_or_create(name=job_type_data["name"])
            queryset.add(job_type)
        serializer = self.get_serializer(queryset.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
    pagination_class = DefaultPagination

    def get_queryset(self):
        """
        Returns the queryset of Talent objects based on the provided query parameters.

        The queryset is filtered by job types if 'skills' are provided in the query parameters.
        It can also be sorted by average rating if 'sort_by' is provided in the query parameters.

        Returns:
            queryset (QuerySet): The filtered and sorted queryset of Talent objects.
        """
        queryset = Talent.objects.all()

        # Filter by job types if provided in query parameters
        skills = self.request.query_params.getlist("skills")
        if skills:
            query_condition = Q()
            for skill in skills:
                query_condition |= Q(skills__name__iexact=skill)
            queryset = queryset.filter(query_condition)

        # Sort by average rating if 'sort_by' is provided in query parameters
        sort_by = self.request.query_params.get("sort_by")
        if sort_by == "most_experienced":
            # Use annotation to get the average rating and order by it
            queryset = queryset.annotate(average_rating=Avg("review__rating")).order_by(
                "-average_rating"
            )
        elif sort_by == "least_experienced":
            # Use annotation to get the average rating and order by it
            queryset = queryset.annotate(average_rating=Avg("review__rating")).order_by(
                "average_rating"
            )

        return queryset


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
        if self.request is None or self.request.method in permissions.SAFE_METHODS:
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
        if self.request is None or self.request.method in permissions.SAFE_METHODS:
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
        if self.request is None or self.request.method in permissions.SAFE_METHODS:
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
        if self.request is None or self.request.method in permissions.SAFE_METHODS:
            return []
        return super().get_authenticators()


# Views for Review endpoints
class ReviewList(generics.ListCreateAPIView):
    """
    API view for listing and creating review instances.

    Attributes:
        queryset (QuerySet): The queryset of Review objects.
        serializer_class (Serializer): The serializer class for Review objects.
        authentication_classes (list): The list of authentication classes used for authentication.

    Methods:
        get_authenticators: Returns the list of authenticators based on the request method.
        perform_create: Performs the creation of a new review instance.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]

    def get_authenticators(self):
        if self.request is None or self.request.method in permissions.SAFE_METHODS:
            return []
        return super().get_authenticators()

    def perform_create(self, serializer):
        """
        Perform custom creation logic for the view.

        This method is called when a new object is being created.
        It checks if the request user is an instance of the Company model.
        If not, it returns a 403 Forbidden response.
        Otherwise, it saves the serializer with the reviewer_organization set to the request user.

        Args:
            serializer (Serializer): The serializer instance.

        Returns:
            Response: The HTTP response.
        """
        if not isinstance(self.request.user, Company):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save(reviewer_organization=self.request.user)


class ReviewDetail(generics.RetrieveAPIView):
    """
    Retrieve a single review instance.

    This view retrieves a single review instance based on the provided ID.
    It does not require authentication.

    Attributes:
        queryset (QuerySet): The queryset of all review instances.
        serializer_class (Serializer): The serializer class for review instances.
        authentication_classes (list): The list of authentication classes used for this view.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = []


@api_view(["GET"])
def get_talent_average_rating(request, pk):
    """
    Get the average rating of a talent.

    Args:
        request (Request): The HTTP request object.
        pk (int): The primary key of the talent.

    Returns:
        Response: The HTTP response object containing the average rating of the talent.
    """
    try:
        talent = Talent.objects.get(pk=pk)
    except Talent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response({"average_rating": talent.get_average_rating()})
