from django.db import models
from timezone_field import TimeZoneField
from phonenumber_field.modelfields import PhoneNumberField
from oauth2.managers import TalentOauth2Manager
from jobs.models import Company


# Create your models here.
class Talent(models.Model):
    """
    Represents a talent in the system.
    """

    objects = TalentOauth2Manager()

    id = models.BigAutoField(primary_key=True)
    avatar = models.URLField(max_length=200)
    username = models.CharField(max_length=200, null=True, blank=True)
    discord_id = models.BigIntegerField(null=True, blank=True)
    twitter_id = models.BigIntegerField(null=True, blank=True)
    discord_global_name = models.CharField(max_length=200, null=True, blank=True)
    twitter_global_name = models.CharField(max_length=200, null=True, blank=True)
    timezone = TimeZoneField(
        default="UTC", choices_display="WITH_GMT_OFFSET", use_pytz=True
    )
    signed_in_with = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=[("Discord", "Discord"), ("Twitter", "Twitter")],
    )
    language = models.CharField(max_length=200, default="English")
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

    def get_average_rating(self) -> float:
        """
        Calculates and returns the average rating for the talent.

        Returns:
            float: The average rating.
        """
        # Get all the reviews for this talent
        reviews = Review.objects.filter(talent=self)

        # Calculate the average rating
        average_rating: float = reviews.aggregate(models.Avg("rating"))["rating__avg"]

        return average_rating

    def increment_profile_visits(self):
        """
        Increments the profile visits count for the talent.
        """
        self.profile_visits += 1
        self.save()

    def increment_unique_visits(self, session_key):
        """
        Increments the unique profile visits count for the talent.

        Args:
            session_key (str): The session key of the visitor.
        """
        if not self.uniqueprofilevisit_set.filter(session_key=session_key).exists():
            self.uniqueprofilevisit_set.create(session_key=session_key)
            self.increment_profile_visits()

    @property
    def is_authenticated(self):
        """
        Indicates if the talent is authenticated.

        Returns:
            bool: True if the talent is authenticated, False otherwise.
        """
        return True

    def __str__(self):
        """
        Returns a string representation of the talent.

        Returns:
            str: The string representation of the talent.
        """
        return f"{self.id} - {self.username if self.username else self.global_name}"


class Skill(models.Model):
    """
    Represents a skill that a user can possess.

    Attributes:
        name (str): The name of the skill.
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
        return self.name


class UniqueProfileVisit(models.Model):
    """
    Represents a unique profile visit by a session key to a talent's profile.
    """

    talent = models.ForeignKey("Talent", on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    visit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("talent", "session_key")

    def __str__(self):
        return self.session_key


class Review(models.Model):
    """
    Represents a review for a talent.

    Attributes:
        talent (Talent): The talent being reviewed.
        reviewer_name (str): The name of the reviewer.
        reviewer_position (str, optional): The position of the reviewer.
        reviewer_organization (Company): The organization of the reviewer.
        review (str, optional): The review text.
        rating (int): The rating given by the reviewer.
    """

    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=200)
    reviewer_position = models.CharField(max_length=200, blank=True, null=True)
    reviewer_organization = models.OneToOneField(Company, on_delete=models.CASCADE)
    review = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.reviewer_name} - {self.reviewer_organization}"


class Experience(models.Model):
    """
    Represents a work experience of a talent.

    Attributes:
        talent (ForeignKey): The talent associated with the experience.
        project_logo (ImageField): The logo of the project.
        company_name (CharField): The name of the company.
        role (CharField): The role in the company.
        description (TextField): A description of the experience.
        start_date (DateField): The start date of the experience.
        end_date (DateField): The end date of the experience.
        currently_working (BooleanField): Indicates if the talent is currently working in this experience.
        verified (BooleanField): Indicates if the experience is verified.
        twitter_link (URLField): The Twitter link associated with the experience.
        discord_link (URLField): The Discord link associated with the experience.
    """

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
