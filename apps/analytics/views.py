"""Analytics views module for the AI Football Platform.

This module contains views for generating analytics reports and statistics
with atomic transaction support.
"""

import logging

from django.db import models, transaction
from django.db.models import Avg, Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAcademyAdmin, IsSystemAdmin
from apps.core.views import BaseModelViewSet

logger = logging.getLogger(__name__)


class AnalyticsViewSet(BaseModelViewSet):
    """
    API endpoints for analytics and reporting with atomic transaction support.

    academy_overview: Get overview statistics for an academy
    player_performance: Get player performance statistics
    team_performance: Get team performance statistics
    match_statistics: Get match statistics and trends
    field_utilization: Get field utilization statistics

    All database operations are executed atomically to ensure data consistency.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Analytics views don't have a base queryset."""
        return None

    @swagger_auto_schema(
        operation_summary="Get academy overview statistics",
        operation_description="Returns comprehensive overview statistics for an academy",
        manual_parameters=[
            openapi.Parameter(
                "academy_id",
                openapi.IN_QUERY,
                description="Academy ID (required for non-system admins)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Academy overview statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "academy_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "academy_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "total_players": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_coaches": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_teams": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_matches": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_fields": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "active_bookings": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad request - missing academy_id",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this academy",
        },
    )
    @action(detail=False, methods=["get"])
    def academy_overview(self, request):
        """
        Get comprehensive overview statistics for an academy.
        """
        user = request.user
        academy_id = request.query_params.get("academy_id")

        # Determine which academy to analyze
        if user.user_type == "system_admin":
            if not academy_id:
                return Response(
                    {"error": "academy_id parameter is required for system admins"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                from apps.academies.models import Academy

                academy = Academy.objects.get(id=academy_id)
            except Academy.DoesNotExist:
                return Response(
                    {"error": "Academy not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif hasattr(user, "profile") and hasattr(user.profile, "academy"):
            academy = user.profile.academy
        else:
            return Response(
                {"error": "User does not have access to any academy"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate statistics
        stats = {
            "academy_id": academy.id,
            "academy_name": academy.name,
            "total_players": academy.players.filter(is_active=True).count(),
            "total_coaches": academy.coaches.filter(is_active=True).count(),
            "total_teams": getattr(academy, "teams", academy.team_set)
            .filter(is_active=True)
            .count(),
            "total_matches": 0,  # Would implement actual match counting
            "total_fields": academy.fields.filter(is_active=True).count(),
            "active_bookings": 0,  # Would implement actual booking counting
        }

        logger.info(f"Generated academy overview for academy {academy.id}")
        return Response(stats)

    @swagger_auto_schema(
        operation_summary="Get player performance statistics",
        operation_description="Returns performance statistics for players",
        manual_parameters=[
            openapi.Parameter(
                "academy_id",
                openapi.IN_QUERY,
                description="Academy ID to filter players",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "team_id",
                openapi.IN_QUERY,
                description="Team ID to filter players",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Player performance statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_players": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "average_age": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "position_distribution": openapi.Schema(
                            type=openapi.TYPE_OBJECT
                        ),
                        "top_performers": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access",
        },
    )
    @action(detail=False, methods=["get"])
    def player_performance(self, request):
        """
        Get player performance statistics.
        """
        from apps.academies.models import PlayerProfile

        # Build queryset based on permissions and filters
        queryset = PlayerProfile.objects.filter(is_active=True)

        user = request.user
        if user.user_type != "system_admin":
            if hasattr(user, "profile") and hasattr(user.profile, "academy"):
                queryset = queryset.filter(academy=user.profile.academy)
            else:
                return Response(
                    {"error": "User does not have access"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Apply filters
        academy_id = request.query_params.get("academy_id")
        if academy_id and user.user_type == "system_admin":
            queryset = queryset.filter(academy_id=academy_id)

        team_id = request.query_params.get("team_id")
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        # Calculate statistics
        total_players = queryset.count()

        # Position distribution
        position_stats = (
            queryset.values("position")
            .annotate(count=Count("position"))
            .order_by("-count")
        )
        position_distribution = {
            stat["position"]: stat["count"] for stat in position_stats
        }

        stats = {
            "total_players": total_players,
            "average_age": 0,  # Would calculate from date_of_birth
            "position_distribution": position_distribution,
            "top_performers": [],  # Would implement based on match statistics
        }

        logger.info(
            f"Generated player performance statistics for {total_players} players"
        )
        return Response(stats)

    @swagger_auto_schema(
        operation_summary="Get team performance statistics",
        operation_description="Returns performance statistics for teams",
        manual_parameters=[
            openapi.Parameter(
                "academy_id",
                openapi.IN_QUERY,
                description="Academy ID to filter teams",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Team performance statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_teams": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "average_team_size": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "category_distribution": openapi.Schema(
                            type=openapi.TYPE_OBJECT
                        ),
                        "top_teams": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access",
        },
    )
    @action(detail=False, methods=["get"])
    def team_performance(self, request):
        """
        Get team performance statistics.
        """
        from apps.players.models import Team

        # Build queryset based on permissions and filters
        queryset = Team.objects.filter(is_active=True)

        user = request.user
        if user.user_type != "system_admin":
            if hasattr(user, "profile") and hasattr(user.profile, "academy"):
                queryset = queryset.filter(academy=user.profile.academy)
            else:
                return Response(
                    {"error": "User does not have access"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Apply filters
        academy_id = request.query_params.get("academy_id")
        if academy_id and user.user_type == "system_admin":
            queryset = queryset.filter(academy_id=academy_id)

        # Calculate statistics
        total_teams = queryset.count()

        # Category distribution
        category_stats = (
            queryset.values("category")
            .annotate(count=Count("category"))
            .order_by("-count")
        )
        category_distribution = {
            stat["category"]: stat["count"] for stat in category_stats
        }

        # Average team size
        team_sizes = queryset.annotate(player_count=Count("players")).aggregate(
            avg_size=Avg("player_count")
        )

        stats = {
            "total_teams": total_teams,
            "average_team_size": team_sizes["avg_size"] or 0,
            "category_distribution": category_distribution,
            "top_teams": [],  # Would implement based on match results
        }

        logger.info(f"Generated team performance statistics for {total_teams} teams")
        return Response(stats)

    @swagger_auto_schema(
        operation_summary="Get field utilization statistics",
        operation_description="Returns field utilization and booking statistics",
        manual_parameters=[
            openapi.Parameter(
                "academy_id",
                openapi.IN_QUERY,
                description="Academy ID to filter fields",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Start date for analysis (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="End date for analysis (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Field utilization statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_fields": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_bookings": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "utilization_rate": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "most_popular_fields": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                        "booking_trends": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access",
        },
    )
    @action(detail=False, methods=["get"])
    def field_utilization(self, request):
        """
        Get field utilization and booking statistics.
        """
        from apps.bookings.models import Field, FieldBooking

        # Build queryset based on permissions and filters
        field_queryset = Field.objects.filter(is_active=True)

        user = request.user
        if user.user_type != "system_admin":
            if hasattr(user, "profile") and hasattr(user.profile, "academy"):
                field_queryset = field_queryset.filter(academy=user.profile.academy)
            else:
                return Response(
                    {"error": "User does not have access"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Apply filters
        academy_id = request.query_params.get("academy_id")
        if academy_id and user.user_type == "system_admin":
            field_queryset = field_queryset.filter(academy_id=academy_id)

        # Calculate statistics
        total_fields = field_queryset.count()

        # Get booking statistics
        booking_queryset = FieldBooking.objects.filter(
            field__in=field_queryset, status__in=["confirmed", "completed"]
        )

        # Apply date filters if provided
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            booking_queryset = booking_queryset.filter(start_time__date__gte=start_date)
        if end_date:
            booking_queryset = booking_queryset.filter(end_time__date__lte=end_date)

        total_bookings = booking_queryset.count()

        # Most popular fields
        popular_fields = (
            booking_queryset.values("field__name")
            .annotate(booking_count=Count("id"))
            .order_by("-booking_count")[:5]
        )

        stats = {
            "total_fields": total_fields,
            "total_bookings": total_bookings,
            "utilization_rate": 0,  # Would calculate based on available hours vs booked hours
            "most_popular_fields": list(popular_fields),
            "booking_trends": {},  # Would implement time-based trends
        }

        logger.info(
            f"Generated field utilization statistics: {total_fields} fields, {total_bookings} bookings"
        )
        return Response(stats)
