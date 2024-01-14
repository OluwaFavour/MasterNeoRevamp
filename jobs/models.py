from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CompanyManager


class Company(AbstractBaseUser, PermissionsMixin):
    """
    Represents a company in the system.

    Attributes:
        name (str): The name of the company.
        email (str): The email address of the company.
        password (str): The password of the company.
        logo (str): The URL of the company's logo.
        website (str, optional): The URL of the company's website.
        description (str, optional): A description of the company.
        is_active (bool): Indicates if the company is active.
        is_staff (bool): Indicates if the company is a staff member.

    Methods:
        __str__(): Returns a string representation of the company.
    """

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
    """
    Represents a type of job in the system.

    Attributes:
        name (str): The name of the job type.
    """

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
    """
    Represents a job listing.

    Attributes:
        job_logo (str): The URL of the job logo.
        job_link (str): The URL of the job listing.
        company (Company): The company associated with the job.
        job_title (str): The title of the job.
        location (str): The location of the job.
        time_added (datetime): The date and time when the job was added.
        job_description (str): The description of the job.
        job_types (QuerySet): The types of the job.
    """

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
