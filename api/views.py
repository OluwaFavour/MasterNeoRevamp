from talents.models import Talent, Review, Experience
from jobs.models import Job
from .serializers import (
    JobSerializer,
    TalentSerializer,
    ExperienceSerializer,
    ReviewSerializer,
)
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


# Define an API root view to display available endpoints
@api_view(["GET"])
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


class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete individual job instances
    queryset = Job.objects.all()
    serializer_class = JobSerializer


# Views for Talent endpoints
class TalentList(generics.ListCreateAPIView):
    # List and create talent instances
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer


class TalentDetail(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete individual talent instances
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer

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


# Views for Experience endpoints
class ExperienceList(generics.ListCreateAPIView):
    # List and create experience instances
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer


class ExperienceDetail(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete individual experience instances
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer


# Views for Review endpoints
class ReviewList(generics.ListCreateAPIView):
    # List and create review instances
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    # Retrieve, update, and delete individual review instances
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
