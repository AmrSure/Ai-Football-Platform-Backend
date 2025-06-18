# apps/players/models.py
from django.db import models

from apps.core.models import BaseModel


class PlayerStatistics(BaseModel):
    """
    Player statistics tracking model for season-level performance metrics.
    Aggregates player performance data across multiple matches.

    Relationships:
    - Many-to-One with PlayerProfile in academies app (player)

    Dependencies:
    - BaseModel for common fields
    - PlayerProfile from academies app for the foreign key relationship
    """

    player = models.ForeignKey(
        "academies.PlayerProfile", on_delete=models.CASCADE, related_name="statistics"
    )
    season = models.CharField(max_length=20)  # e.g., "2024-2025"

    # Physical Stats
    matches_played = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)
    goals_scored = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)

    # Performance Metrics (AI-generated)
    speed_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    technique_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tactical_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    fitness_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    overall_rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ["player", "season"]


class Team(BaseModel):
    """
    Team model representing a group of players within an academy.
    Teams participate in matches and are managed by coaches.

    Relationships:
    - Many-to-One with Academy in academies app (academy)
    - Many-to-One with CoachProfile in academies app (coach)
    - Many-to-Many with PlayerProfile in academies app (players)
    - One-to-Many with Match in matches app as home_team (home_matches)
    - One-to-Many with Match in matches app as away_team (away_matches)

    Dependencies:
    - BaseModel for common fields
    - Academy from academies app for the foreign key relationship
    - CoachProfile from academies app for the foreign key relationship
    - PlayerProfile from academies app for the many-to-many relationship
    """

    name = models.CharField(max_length=100)
    academy = models.ForeignKey(
        "academies.Academy", on_delete=models.CASCADE, related_name="teams"
    )
    coach = models.ForeignKey(
        "academies.CoachProfile",
        on_delete=models.SET_NULL,
        null=True,
        related_name="teams",
    )
    players = models.ManyToManyField(
        "academies.PlayerProfile", related_name="teams", blank=True
    )
    age_group = models.CharField(max_length=20)  # U-16, U-18, Senior, etc.
    formation = models.CharField(max_length=20, blank=True)  # 4-4-2, 3-5-2, etc.
