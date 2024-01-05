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
    # Return a response with available API endpoints
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
    # List and create job instances
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    authentication_classes = []


class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete individual job instances
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    authentication_classes = []


# Views for Talent endpoints
class TalentList(generics.ListAPIView):
    # List and create talent instances
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    authentication_classes = []


class TalentDetail(generics.RetrieveDestroyAPIView):
    # Retrieve, update, and delete individual talent instances
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer

    def get_authenticators(self):
        if self.request.method == "GET":
            return []
        return super().get_authenticators()

    # Custom retrieve method to handle incrementing unique profile visits
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Get or create a session key for the current request
        session_key = (
            request.session.session_key
            if hasattr(request.session, "session_key")
            else None
        )
        # Increment profile visits if session key exists
        if session_key:
            instance.increment_unique_visits(session_key)
        return super().retrieve(request, *args, **kwargs)


@api_view(["PATCH"])
def about_me(request, pk, format=None):
    try:
        talent = Talent.objects.get(pk=pk)
    except Talent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AboutMeSerializer(talent, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def summary(request, pk, format=None):
    try:
        talent = Talent.objects.get(pk=pk)
    except Talent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SummarySerializer(talent, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def username(request, pk, format=None):
    try:
        talent = Talent.objects.get(pk=pk)
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
