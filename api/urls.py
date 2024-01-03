from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    TalentList,
    TalentDetail,
    api_root,
    JobDetail,
    JobList,
    ExperienceList,
    ExperienceDetail,
    ReviewList,
    ReviewDetail,
)

urlpatterns = [
    path("", api_root, name="api-root"),
    path("talent/", TalentList.as_view(), name="talent-list"),
    path("talent/<int:pk>/", TalentDetail.as_view(), name="talent-detail"),
    path("job/", JobList.as_view(), name="job-list"),
    path("job/<int:pk>/", JobDetail.as_view(), name="job-detail"),
    path("experience/", ExperienceList.as_view(), name="experience-list"),
    path("experience/<int:pk>/", ExperienceDetail.as_view(), name="experience-detail"),
    path("review/", ReviewList.as_view(), name="review-list"),
    path("review/<int:pk>/", ReviewDetail.as_view(), name="review-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
