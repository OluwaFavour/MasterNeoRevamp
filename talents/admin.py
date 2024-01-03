from django.contrib import admin
from .models import Talent, Review, Experience, UniqueProfileVisit


# Register your models here.
@admin.register(Talent)
class TalentAdmin(admin.ModelAdmin):
    list_display = ("username", "timezone", "language", "profile_visits", "date_joined")


admin.site.register(Review)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("talent", "project_logo", "role", "description")


@admin.register(UniqueProfileVisit)
class UniqueProfileVisitAdmin(admin.ModelAdmin):
    list_display = ("talent", "session_key", "visit_date")
