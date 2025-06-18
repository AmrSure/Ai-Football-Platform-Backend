# apps/matches/models.py
from django.db import models

from apps.core.models import BaseModel


class Match(BaseModel):
    """
    Match model representing a football match between teams.
    Stores match details, results, and provides links to video analysis.

    Relationships:
    - Many-to-One with Team in players app as home_team
    - Many-to-One with Team in players app as away_team (optional for training matches)
    - Many-to-One with Field in bookings app (venue)
    - One-to-One with FieldBooking in bookings app (match)
    - One-to-Many with MatchPerformance (performances)

    Dependencies:
    - BaseModel for common fields
    - Team from players app for the foreign key relationships
    - Field from bookings app for the foreign key relationship
    """

    MATCH_TYPES = (
        ("friendly", "Friendly"),
        ("league", "League"),
        ("cup", "Cup"),
        ("training", "Training"),
    )

    home_team = models.ForeignKey(
        "players.Team", on_delete=models.CASCADE, related_name="home_matches"
    )
    away_team = models.ForeignKey(
        "players.Team",
        on_delete=models.CASCADE,
        related_name="away_matches",
        null=True,
        blank=True,
    )
    match_type = models.CharField(max_length=20, choices=MATCH_TYPES)
    date_time = models.DateTimeField()
    venue = models.ForeignKey(
        "bookings.Field", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Match Results
    is_completed = models.BooleanField(default=False)
    home_score = models.PositiveIntegerField(null=True, blank=True)
    away_score = models.PositiveIntegerField(null=True, blank=True)

    # Video Analysis
    original_video = models.FileField(
        upload_to="matches/videos/original/", null=True, blank=True
    )
    processed_video = models.FileField(
        upload_to="matches/videos/processed/", null=True, blank=True
    )
    analysis_completed = models.BooleanField(default=False)
    analysis_report = models.JSONField(null=True, blank=True)


class MatchPerformance(BaseModel):
    """
    Individual player performance in a match.
    Tracks statistics and AI-generated performance metrics for a player in a specific match.

    Relationships:
    - Many-to-One with Match (match)
    - Many-to-One with PlayerProfile in academies app (player)

    Dependencies:
    - BaseModel for common fields
    - Match model for the foreign key relationship
    - PlayerProfile from academies app for the foreign key relationship
    """

    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="performances"
    )
    player = models.ForeignKey(
        "academies.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="match_performances",
    )

    # Match-specific stats
    minutes_played = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    passes_completed = models.PositiveIntegerField(default=0)
    passes_attempted = models.PositiveIntegerField(default=0)

    # AI-generated performance scores
    performance_rating = models.DecimalField(
        max_digits=4, decimal_places=2, default=0.00
    )
    ai_analysis_data = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ["match", "player"]
