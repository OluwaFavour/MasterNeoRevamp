from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CompanyManager


class Company(AbstractBaseUser, PermissionsMixin):
    objects = CompanyManager()

    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    logo = models.URLField(max_length=200)
    website = models.URLField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    def __str__(self):
        return f"{self.name}"


class JobType(models.Model):
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
        return f"{self.name}"


class Job(models.Model):
    job_logo = models.URLField(max_length=200)
    job_link = models.URLField(max_length=200)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    location = models.CharField(max_length=200, default="Remote")
    time_added = models.DateTimeField(auto_now=True, editable=False)
    job_description = models.TextField()
    job_types = models.ManyToManyField("JobType", related_name="job_types")

    def __str__(self):
        return f"{self.company.name} - {self.job_title}"
