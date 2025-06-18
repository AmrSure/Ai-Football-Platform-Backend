from django.contrib import admin

from apps.core.admin import AcademyScopedAdmin

from .models import Match, MatchPerformance


@admin.register(Match)
class MatchAdmin(AcademyScopedAdmin):
    """
    Admin configuration for Match model.
    Provides match scheduling, results tracking, and video analysis management.
    """

    list_display = [
        "id",
        "match_type",
        "home_team",
        "away_team",
        "date_time",
        "venue",
        "match_result",
        "is_completed",
        "is_active",
    ]
    list_filter = [
        "is_active",
        "is_completed",
        "match_type",
        "date_time",
        "home_team__academy",
        "analysis_completed",
    ]
    search_fields = ["home_team__name", "away_team__name", "venue__name"]
    raw_id_fields = ["home_team", "away_team", "venue"]
    date_hierarchy = "date_time"

    fieldsets = (
        (
            "Match Information",
            {"fields": ("match_type", "home_team", "away_team", "date_time", "venue")},
        ),
        ("Match Results", {"fields": ("is_completed", "home_score", "away_score")}),
        (
            "Video Analysis",
            {
                "fields": (
                    "original_video",
                    "processed_video",
                    "analysis_completed",
                    "analysis_report",
                )
            },
        ),
        ("Status", {"fields": ("is_active",)}),
    )

    def match_result(self, obj):
        """Display match result or scheduled status"""
        if obj.is_completed:
            return f"{obj.home_score} - {obj.away_score}"
        return "Scheduled"

    match_result.short_description = "Result"

    def get_queryset(self, request):
        """Filter matches based on academy access"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, "profile") and hasattr(
            request.user.profile, "academy"
        ):
            academy = request.user.profile.academy
            return qs.filter(home_team__academy=academy) | qs.filter(
                away_team__academy=academy
            )
        return qs.none()


@admin.register(MatchPerformance)
class MatchPerformanceAdmin(AcademyScopedAdmin):
    """
    Admin configuration for MatchPerformance model.
    Tracks individual player performance in matches with AI analysis.
    """

    list_display = [
        "id",
        "match",
        "player",
        "minutes_played",
        "goals",
        "assists",
        "performance_rating",
        "is_active",
    ]
    list_filter = ["is_active", "match__match_type", "player__academy"]
    search_fields = [
        "player__user__username",
        "player__user__first_name",
        "player__user__last_name",
        "match__home_team__name",
    ]
    raw_id_fields = ["match", "player"]

    fieldsets = (
        ("Performance Information", {"fields": ("match", "player")}),
        (
            "Match Statistics",
            {
                "fields": (
                    "minutes_played",
                    "goals",
                    "assists",
                    "passes_completed",
                    "passes_attempted",
                )
            },
        ),
        ("AI Analysis", {"fields": ("performance_rating", "ai_analysis_data")}),
        ("Status", {"fields": ("is_active",)}),
    )

    def get_queryset(self, request):
        """Filter performance records based on academy access"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, "profile") and hasattr(
            request.user.profile, "academy"
        ):
            return qs.filter(player__academy=request.user.profile.academy)
        return qs.none()
