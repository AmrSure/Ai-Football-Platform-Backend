"""Serializers for the matches app."""

from rest_framework import serializers

from apps.core.serializers import BaseModelSerializer

from .models import Match, MatchPerformance


class MatchSerializer(BaseModelSerializer):
    """Serializer for Match model."""

    home_team_name = serializers.CharField(source="home_team.name", read_only=True)
    away_team_name = serializers.CharField(source="away_team.name", read_only=True)
    venue_name = serializers.CharField(source="venue.name", read_only=True)
    status = serializers.SerializerMethodField()
    final_score = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "id",
            "home_team",
            "home_team_name",
            "away_team",
            "away_team_name",
            "match_type",
            "date_time",
            "venue",
            "venue_name",
            "is_completed",
            "home_score",
            "away_score",
            "status",
            "final_score",
            "original_video",
            "processed_video",
            "analysis_completed",
            "analysis_report",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "analysis_completed",
            "processed_video",
        ]

    def get_status(self, obj):
        """Get match status based on completion and scores."""
        if obj.is_completed:
            return "completed"
        elif obj.home_score is not None or obj.away_score is not None:
            return "in_progress"
        else:
            return "scheduled"

    def get_final_score(self, obj):
        """Get final score string if match is completed."""
        if (
            obj.is_completed
            and obj.home_score is not None
            and obj.away_score is not None
        ):
            return f"{obj.home_score} - {obj.away_score}"
        return None


class MatchPerformanceSerializer(BaseModelSerializer):
    """Serializer for MatchPerformance model."""

    player_name = serializers.CharField(
        source="player.user.get_full_name", read_only=True
    )
    match_details = serializers.CharField(source="match.__str__", read_only=True)
    pass_accuracy = serializers.SerializerMethodField()

    class Meta:
        model = MatchPerformance
        fields = [
            "id",
            "match",
            "match_details",
            "player",
            "player_name",
            "minutes_played",
            "goals",
            "assists",
            "passes_completed",
            "passes_attempted",
            "pass_accuracy",
            "performance_rating",
            "ai_analysis_data",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_pass_accuracy(self, obj):
        """Calculate pass accuracy percentage."""
        if obj.passes_attempted > 0:
            return round((obj.passes_completed / obj.passes_attempted) * 100, 2)
        return 0.0
