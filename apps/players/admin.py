from django.contrib import admin

from apps.core.admin import AcademyScopedAdmin

from .models import PlayerStatistics, Team


@admin.register(PlayerStatistics)
class PlayerStatisticsAdmin(AcademyScopedAdmin):
    """
    Admin configuration for PlayerStatistics model.
    Displays player performance metrics with filtering and search.
    """

    list_display = [
        "id",
        "player",
        "season",
        "matches_played",
        "goals_scored",
        "assists",
        "overall_rating",
        "is_active",
    ]
    list_filter = ["is_active", "season", "player__academy"]
    search_fields = [
        "player__user__username",
        "player__user__first_name",
        "player__user__last_name",
    ]
    raw_id_fields = ["player"]

    fieldsets = (
        ("Player Information", {"fields": ("player", "season")}),
        (
            "Match Statistics",
            {
                "fields": (
                    "matches_played",
                    "minutes_played",
                    "goals_scored",
                    "assists",
                    "yellow_cards",
                    "red_cards",
                )
            },
        ),
        (
            "Performance Metrics",
            {
                "fields": (
                    "speed_score",
                    "technique_score",
                    "tactical_score",
                    "fitness_score",
                    "overall_rating",
                )
            },
        ),
        ("Status", {"fields": ("is_active",)}),
    )

    def get_queryset(self, request):
        """Filter statistics based on academy access"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, "profile") and hasattr(
            request.user.profile, "academy"
        ):
            return qs.filter(player__academy=request.user.profile.academy)
        return qs.none()


@admin.register(Team)
class TeamAdmin(AcademyScopedAdmin):
    """
    Admin configuration for Team model.
    Provides management of teams with player and coach assignments.
    """

    list_display = [
        "id",
        "name",
        "academy",
        "coach",
        "age_group",
        "formation",
        "is_active",
    ]
    list_filter = ["is_active", "academy", "age_group"]
    search_fields = [
        "name",
        "coach__user__username",
        "coach__user__first_name",
        "coach__user__last_name",
    ]
    raw_id_fields = ["academy", "coach"]
    filter_horizontal = ["players"]

    fieldsets = (
        (
            "Team Information",
            {"fields": ("name", "academy", "coach", "age_group", "formation")},
        ),
        ("Players", {"fields": ("players",)}),
        ("Status", {"fields": ("is_active",)}),
    )
