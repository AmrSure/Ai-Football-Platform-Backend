from django.db import models

from apps.core.models import BaseModel, UserProfile


class Academy(BaseModel):
    """
    Academy model representing a football academy organization.
    Central entity that connects coaches, players, teams, and fields.

    Relationships:
    - One-to-Many with AcademyAdminProfile (admins)
    - One-to-Many with CoachProfile (coaches)
    - One-to-Many with PlayerProfile (players)
    - One-to-Many with Team in players app (teams)
    - One-to-Many with Field in bookings app (fields)

    Dependencies:
    - BaseModel for common fields
    """

    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="academies/logos/", blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)
    established_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Academies"
        db_table = "academies_academy"


class AcademyAdminProfile(UserProfile):
    """
    Profile for academy administrators.
    Manages an academy and has administrative privileges.

    Relationships:
    - Many-to-One with Academy
    - Inherits One-to-One with User from UserProfile

    Dependencies:
    - UserProfile as parent class
    - Academy model for the foreign key relationship
    """

    academy = models.ForeignKey(
        Academy, on_delete=models.CASCADE, related_name="admins"
    )
    position = models.CharField(max_length=100, blank=True)


class CoachProfile(UserProfile):
    """
    Profile for coaches in an academy.
    Coaches manage teams and training sessions.

    Relationships:
    - Many-to-One with Academy
    - One-to-Many with Team in players app (teams)
    - Inherits One-to-One with User from UserProfile

    Dependencies:
    - UserProfile as parent class
    - Academy model for the foreign key relationship
    """

    academy = models.ForeignKey(
        Academy, on_delete=models.CASCADE, related_name="coaches"
    )
    specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    certification = models.CharField(max_length=200, blank=True)


class PlayerProfile(UserProfile):
    """
    Profile for players in an academy.
    Players are part of teams and participate in matches.

    Relationships:
    - Many-to-One with Academy
    - Many-to-Many with Team in players app (teams)
    - One-to-Many with PlayerStatistics in players app (statistics)
    - One-to-Many with MatchPerformance in matches app (match_performances)
    - Many-to-Many with ParentProfile (parents)
    - Inherits One-to-One with User from UserProfile

    Dependencies:
    - UserProfile as parent class
    - Academy model for the foreign key relationship
    """

    academy = models.ForeignKey(
        Academy, on_delete=models.CASCADE, related_name="players"
    )
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    position = models.CharField(max_length=50, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dominant_foot = models.CharField(
        max_length=10,
        choices=[("left", "Left"), ("right", "Right"), ("both", "Both")],
        blank=True,
    )


class ParentProfile(UserProfile):
    """
    Profile for parents of players.
    Parents can monitor their children's progress and activities.

    Relationships:
    - Many-to-Many with PlayerProfile (children)
    - Inherits One-to-One with User from UserProfile

    Dependencies:
    - UserProfile as parent class
    - PlayerProfile for the many-to-many relationship
    """

    children = models.ManyToManyField(PlayerProfile, related_name="parents", blank=True)
    relationship = models.CharField(
        max_length=20,
        choices=[("father", "Father"), ("mother", "Mother"), ("guardian", "Guardian")],
    )


class ExternalClientProfile(UserProfile):
    """
    Profile for external clients who can book academy facilities.
    These are users outside the academy structure who use facilities.

    Relationships:
    - Inherits One-to-One with User from UserProfile
    - Indirectly related to FieldBooking in bookings app through User

    Dependencies:
    - UserProfile as parent class
    """

    organization = models.CharField(max_length=200, blank=True)
    preferred_sports = models.CharField(max_length=200, blank=True)
