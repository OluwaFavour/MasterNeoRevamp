from django.db import models
from timezone_field import TimeZoneField
from phonenumber_field.modelfields import PhoneNumberField
from oauth2.managers import TalentOauth2Manager


# Create your models here.
class Talent(models.Model):
    objects = TalentOauth2Manager()

    id = models.BigIntegerField(primary_key=True)
    avatar = models.URLField(max_length=200)
    username = models.CharField(max_length=200)
    global_name = models.CharField(max_length=200)
    timezone = TimeZoneField(
        default="UTC", choices_display="WITH_GMT_OFFSET", use_pytz=True
    )
    language = models.CharField(max_length=200)
    about_me = models.TextField()
    summary = models.TextField()
    profile_visits = models.PositiveIntegerField(default=0, editable=False)
    email = models.EmailField(max_length=200, null=True, blank=True)
    discord_profile = models.CharField(max_length=200, null=True, blank=True)
    twitter_profile = models.CharField(max_length=200, null=True, blank=True)
    phone_number = PhoneNumberField(blank=True)
    date_joined = models.DateTimeField(auto_now=True, editable=False)
    last_login = models.DateTimeField(editable=False, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    skills = models.ManyToManyField("Skill", blank=True)

    def increment_profile_visits(self):
        self.profile_visits += 1
        self.save()

    def increment_unique_visits(self, session_key):
        if not self.uniqueprofilevisit_set.filter(session_key=session_key).exists():
            self.uniqueprofilevisit_set.create(session_key=session_key)
            self.increment_profile_visits()

    def is_authenticated(self, request):
        return True

    def __str__(self):
        return self.username


class Skill(models.Model):
    SKILL_CHOICES = [
        ("Community manager", "Community manager"),
        ("Collab manager", "Collab manager"),
        ("Community engagement", "Community engagement"),
        ("Security expert", "Security expert"),
        ("Marketer", "Marketer"),
        ("Moderator", "Moderator"),
        ("Event planning", "Event planning"),
        ("Social media management", "Social media management"),
        ("Influencer", "Influencer"),
        ("Marketer", "Marketer"),
        ("Project advisor", "Project advisor"),
    ]

    name = models.CharField(max_length=200, choices=SKILL_CHOICES, unique=True)

    def __str__(self):
        return self.name

class UniqueProfileVisit(models.Model):
    talent = models.ForeignKey("Talent", on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    visit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("talent", "session_key")

    def __str__(self):
        return self.session_key


class Review(models.Model):
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=200)
    reviewer_organization = models.CharField(max_length=200)
    review = models.TextField()
    rating = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.reviewer_name} - {self.reviewer_organization}"


class Experience(models.Model):
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)
    project_logo = models.ImageField(upload_to="images/")
    company_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    currently_working = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    twitter_link = models.URLField(max_length=200)
    discord_link = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.role} - {self.company_name}"
