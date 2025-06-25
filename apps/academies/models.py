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

    def __str__(self):
        """Return string representation of the academy."""
        return self.name

    @property
    def basic_statistics(self):
        """Get basic statistics for the academy."""
        return {
            "total_coaches": self.coaches.filter(is_active=True).count(),
            "total_players": self.players.filter(is_active=True).count(),
            "total_teams": self.teams.filter(is_active=True).count(),
            "total_fields": self.fields.filter(is_active=True).count(),
        }

    @property
    def statistics(self):
        """Get comprehensive statistics for the academy."""
        # Get active counts
        active_coaches = self.coaches.filter(is_active=True)
        active_players = self.players.filter(is_active=True)
        active_teams = (
            self.teams.filter(is_active=True) if hasattr(self, "teams") else []
        )
        active_fields = self.fields.filter(is_active=True)

        # Build detailed statistics similar to AcademyDetailSerializer
        stats = {
            "total_coaches": active_coaches.count(),
            "total_players": active_players.count(),
            "total_teams": len(active_teams)
            if hasattr(active_teams, "__len__")
            else active_teams.count(),
            "total_fields": active_fields.count(),
            "coaches_by_specialization": self._get_coaches_by_specialization(
                active_coaches
            ),
            "players_by_position": self._get_players_by_position(active_players),
            "teams_by_age_group": self._get_teams_by_age_group(active_teams),
            "fields_by_type": self._get_fields_by_type(active_fields),
        }

        return stats

    def _get_coaches_by_specialization(self, coaches):
        """Group coaches by specialization."""
        specializations = {}
        for coach in coaches:
            spec = coach.specialization or "Not Specified"
            specializations[spec] = specializations.get(spec, 0) + 1
        return specializations

    def _get_players_by_position(self, players):
        """Group players by position."""
        positions = {}
        for player in players:
            pos = player.position or "Not Specified"
            positions[pos] = positions.get(pos, 0) + 1
        return positions

    def _get_teams_by_age_group(self, teams):
        """Group teams by age group."""
        age_groups = {}
        for team in teams:
            age_group = team.age_group or "Not Specified"
            age_groups[age_group] = age_groups.get(age_group, 0) + 1
        return age_groups

    def _get_fields_by_type(self, fields):
        """Group fields by type."""
        field_types = {}
        for field in fields:
            field_type = field.field_type if field.field_type else "Not Specified"
            field_types[field_type] = field_types.get(field_type, 0) + 1
        return field_types

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
        Academy, on_delete=models.CASCADE, related_name="admins", null=True, blank=True
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
        Academy, on_delete=models.CASCADE, related_name="coaches", null=True, blank=True
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
        Academy, on_delete=models.CASCADE, related_name="players", null=True, blank=True
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
