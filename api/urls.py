from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    TalentList,
    TalentDetail,
    APIRoot,
    JobDetail,
    JobList,
    JobTypeView,
    ExperienceList,
    ExperienceDetail,
    ReviewList,
    ReviewDetail,
    SkillView,
    username,
    about_me,
    summary,
    get_talent_average_rating,
    upload_avatar,
    language,
    timezone,
)

urlpatterns = [
    path("", APIRoot.as_view(), name="api-root"),
    path("talent/", TalentList.as_view(), name="talent-list"),
    path("talent/<int:pk>/", TalentDetail.as_view(), name="talent-detail"),
    path("talent/<int:pk>/skills/", SkillView.as_view(), name="skill-list"),
    path("talent/<int:pk>/about-me/", about_me, name="about-me"),
    path("talent/<int:pk>/summary/", summary, name="summary"),
    path("talent/<int:pk>/username/", username, name="username"),
    path("talent/<int:pk>/average-rating/", get_talent_average_rating, name="average-rating"),
    path("talent/<int:pk>/avatar/", upload_avatar, name="avatar"),
    path("talent/<int:pk>/language/", language, name="language"),
    path("talent/<int:pk>/timezone/", timezone, name="timezone"),
    path("job/", JobList.as_view(), name="job-list"),
    path("job/<int:pk>/", JobDetail.as_view(), name="job-detail"),
    path("job/<int:pk>/job_type/", JobTypeView.as_view(), name="job-type"),
    path("experience/", ExperienceList.as_view(), name="experience-list"),
    path("experience/<int:pk>/", ExperienceDetail.as_view(), name="experience-detail"),
    path("review/", ReviewList.as_view(), name="review-list"),
    path("review/<int:pk>/", ReviewDetail.as_view(), name="review-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
