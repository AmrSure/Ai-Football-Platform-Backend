"""Core views module for the AI Football Platform.

This module contains base viewsets and view mixins used across the application.
It provides consistent API behavior and utility functions for REST endpoints.
"""

import logging

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base viewset with common functionality for all model viewsets.

    Provides filtering, searching, ordering, and active status handling with
    atomic transaction support for all database operations.

    Features:
    - Filters out inactive objects by default
    - Automatically sets created_by to current user if model supports it
    - Provides toggle_active action to enable/disable objects
    - Includes common filter backends
    - Atomic transactions for all write operations
    - Proper error logging and handling

    Dependencies:
    - Django REST Framework's ModelViewSet
    - DjangoFilterBackend, SearchFilter, OrderingFilter for query filtering
    - Django's transaction module for atomic operations
    """

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Default ordering will be set in get_queryset based on available fields

    def get_queryset(self):
        """
        Override to filter out inactive objects by default.

        Only returns objects where is_active=True if the model has that field.
        Also sets appropriate ordering based on available date fields.
        """
        queryset = super().get_queryset()

        # Apply default ordering based on available fields
        model = queryset.model
        if not self.ordering:
            if hasattr(model, "created_at"):
                queryset = queryset.order_by("-created_at")
            elif hasattr(model, "date_joined"):
                queryset = queryset.order_by("-date_joined")
            elif hasattr(model, "date_created"):
                queryset = queryset.order_by("-date_created")
            elif hasattr(model, "updated_at"):
                queryset = queryset.order_by("-updated_at")

        # Filter by active status if applicable
        if hasattr(model, "is_active"):
            queryset = queryset.filter(is_active=True)

        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new object with atomic transaction.

        Ensures that all database operations during object creation
        are executed atomically to maintain data consistency.
        """
        try:
            logger.info(
                f"Creating new {self.get_serializer().Meta.model.__name__} by user {request.user.id}"
            )
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error creating {self.get_serializer().Meta.model.__name__}: {str(e)}"
            )
            raise

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update an object with atomic transaction.

        Ensures that all database operations during object update
        are executed atomically to maintain data consistency.
        """
        try:
            obj = self.get_object()
            logger.info(
                f"Updating {obj.__class__.__name__} {obj.pk} by user {request.user.id}"
            )
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error updating object: {str(e)}")
            raise

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an object with atomic transaction.

        Ensures that all database operations during object partial update
        are executed atomically to maintain data consistency.
        """
        try:
            obj = self.get_object()
            logger.info(
                f"Partially updating {obj.__class__.__name__} {obj.pk} by user {request.user.id}"
            )
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error partially updating object: {str(e)}")
            raise

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Delete an object with atomic transaction.

        Ensures that all database operations during object deletion
        are executed atomically to maintain data consistency.
        """
        try:
            obj = self.get_object()
            logger.info(
                f"Deleting {obj.__class__.__name__} {obj.pk} by user {request.user.id}"
            )
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error deleting object: {str(e)}")
            raise

    def perform_create(self, serializer):
        """
        Override to automatically set created_by field to current user.

        Only sets the field if the model has a created_by field.
        Executed within the atomic transaction of the create method.
        """
        if hasattr(serializer.Meta.model, "created_by"):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Toggle active status of object with atomic transaction.

        Provides an endpoint to enable/disable objects without deleting them.
        All operations are executed atomically to ensure consistency.
        """
        try:
            obj = self.get_object()
            if hasattr(obj, "is_active"):
                old_status = obj.is_active
                obj.is_active = not obj.is_active
                obj.save()
                status_value = "active" if obj.is_active else "inactive"
                logger.info(
                    f"Toggled {obj.__class__.__name__} {obj.pk} from {old_status} to {obj.is_active}"
                )
                return Response({"status": status_value})
            return Response(
                {"error": "Object does not support active status"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error toggling active status: {str(e)}")
            raise


class AcademyScopedViewSet(BaseModelViewSet):
    """
    Base viewset for academy-scoped resources with atomic transaction support.

    Filters queryset based on user's academy access permissions and ensures
    all database operations are executed atomically.

    Features:
    - System admins see all resources
    - Academy users only see resources from their academy
    - Other users see no resources
    - Atomic transactions for all write operations
    - Proper error logging and handling

    Dependencies:
    - BaseModelViewSet as parent class
    - User model with user_type and profile relationship
    - Django's transaction module for atomic operations
    """

    def get_queryset(self):
        """
        Override to filter queryset based on user's academy access.

        Implements academy-level access control.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == "system_admin":
            return queryset
        elif hasattr(user, "profile") and hasattr(user.profile, "academy"):
            return queryset.filter(academy=user.profile.academy)
        return queryset.none()


class DashboardStatsView(APIView):
    """
    Dashboard statistics endpoint that auto-detects user type and returns appropriate stats.

    For system_admin:
    - Returns system-wide statistics across all academies

    For academy_admin:
    - Returns statistics scoped to their specific academy

    For coach:
    - Returns statistics related to their teams, players, and matches

    For external_client:
    - Returns booking history and statistics for their bookings
    """

    @swagger_auto_schema(
        operation_summary="Get dashboard statistics",
        operation_description="Returns dashboard statistics based on user type. System admins get system-wide stats, academy admins get academy-specific stats, coaches get their team-related stats, external clients get their booking history and statistics.",
        responses={
            200: openapi.Response(
                description="Dashboard statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "academies_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "coaches_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "players_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "parents_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "external_clients_count": openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                        "fields_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "bookings_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "teams_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "matches_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_bookings": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "upcoming_bookings": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "completed_bookings": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "cancelled_bookings": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_spent": openapi.Schema(type=openapi.TYPE_STRING),
                        "favorite_academies": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                        "recent_bookings": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - insufficient permissions",
        },
    )
    def get(self, request):
        """Get dashboard statistics based on user type."""
        user = request.user
        user_type = user.user_type

        if user_type == "system_admin":
            return self._get_system_admin_stats()
        elif user_type == "academy_admin":
            return self._get_academy_admin_stats(user)
        elif user_type == "coach":
            return self._get_coach_stats(user)
        elif user_type == "external_client":
            return self._get_external_client_stats(user)
        else:
            return Response(
                {
                    "detail": "Dashboard stats are only available for system admins, academy admins, coaches, and external clients."
                },
                status=403,
            )

    def _get_system_admin_stats(self):
        """Get system-wide statistics for system admins."""
        from apps.academies.models import (
            Academy,
            CoachProfile,
            ExternalClientProfile,
            ParentProfile,
            PlayerProfile,
        )
        from apps.bookings.models import Field, FieldBooking

        # Get all active profiles
        active_coaches = CoachProfile.objects.filter(is_active=True)
        active_players = PlayerProfile.objects.filter(is_active=True)
        active_parents = ParentProfile.objects.filter(is_active=True)
        active_external_clients = ExternalClientProfile.objects.filter(is_active=True)
        active_fields = Field.objects.filter(is_active=True)
        active_bookings = FieldBooking.objects.filter(is_active=True)

        stats = {
            "user_type": "system_admin",
            "academies_count": Academy.objects.filter(is_active=True).count(),
            "coaches_count": active_coaches.count(),
            "players_count": active_players.count(),
            "parents_count": active_parents.count(),
            "external_clients_count": active_external_clients.count(),
            "fields_count": active_fields.count(),
            "bookings_count": active_bookings.count(),
        }

        logger.info("Retrieved system-wide dashboard stats")
        return Response(stats)

    def _get_academy_admin_stats(self, user):
        """Get academy-specific statistics for academy admins."""
        from apps.academies.models import (
            CoachProfile,
            ExternalClientProfile,
            ParentProfile,
            PlayerProfile,
        )
        from apps.bookings.models import Field, FieldBooking

        # Check if user has academy profile
        if not hasattr(user, "profile") or not hasattr(user.profile, "academy"):
            return Response(
                {
                    "detail": "Academy admin profile not found or not associated with an academy."
                },
                status=400,
            )

        academy = user.profile.academy
        if not academy:
            return Response(
                {"detail": "Academy admin is not associated with any academy."},
                status=400,
            )

        # Get academy-specific statistics
        academy_coaches = CoachProfile.objects.filter(academy=academy, is_active=True)
        academy_players = PlayerProfile.objects.filter(academy=academy, is_active=True)
        academy_fields = Field.objects.filter(academy=academy, is_active=True)
        academy_bookings = FieldBooking.objects.filter(
            field__academy=academy, is_active=True
        )

        # Get parents count (related through players)
        parent_ids = set()
        for player in academy_players:
            for parent in player.parents.filter(is_active=True):
                parent_ids.add(parent.id)

        # Get external clients who have booked fields at this academy
        external_client_ids = set()
        for booking in academy_bookings:
            if booking.booked_by.user_type == "external_client":
                external_client_ids.add(booking.booked_by.id)

        stats = {
            "user_type": "academy_admin",
            "academy_id": academy.id,
            "academy_name": academy.name,
            "coaches_count": academy_coaches.count(),
            "players_count": academy_players.count(),
            "parents_count": len(parent_ids),
            "external_clients_count": len(external_client_ids),
            "fields_count": academy_fields.count(),
            "bookings_count": academy_bookings.count(),
        }

        logger.info(
            f"Retrieved academy dashboard stats for academy {academy.id} by user {user.email}"
        )
        return Response(stats)

    def _get_coach_stats(self, user):
        """Get team-related statistics for coaches."""
        from apps.matches.models import Match
        from apps.players.models import Team

        # Check if user has coach profile
        if not hasattr(user, "profile"):
            return Response({"detail": "Coach profile not found."}, status=400)

        coach_profile = user.profile

        # Get teams coached by this coach
        teams = Team.objects.filter(coach=coach_profile, is_active=True)

        # Get all players from coach's teams
        total_players = 0
        for team in teams:
            total_players += team.players.filter(is_active=True).count()

        # Get matches where coach's teams are involved
        matches = Match.objects.filter(is_active=True).filter(
            models.Q(home_team__in=teams) | models.Q(away_team__in=teams)
        )

        stats = {
            "user_type": "coach",
            "academy_id": coach_profile.academy.id if coach_profile.academy else None,
            "academy_name": coach_profile.academy.name
            if coach_profile.academy
            else None,
            "teams_count": teams.count(),
            "players_count": total_players,
            "matches_count": matches.count(),
        }

        logger.info(f"Retrieved coach dashboard stats for coach {user.email}")
        return Response(stats)

    def _get_external_client_stats(self, user):
        """Get booking history and statistics for external clients."""
        from decimal import Decimal

        from django.utils import timezone

        from apps.bookings.models import FieldBooking

        # Get all bookings for this external client
        all_bookings = FieldBooking.objects.filter(
            booked_by=user, is_active=True
        ).select_related("field", "field__academy")

        # Calculate booking statistics
        total_bookings = all_bookings.count()

        # Get current time for filtering
        now = timezone.now()

        # Upcoming bookings (future bookings)
        upcoming_bookings = all_bookings.filter(
            start_time__gt=now, status__in=["pending", "confirmed"]
        ).count()

        # Completed bookings (past bookings with completed status)
        completed_bookings = all_bookings.filter(status="completed").count()

        # Cancelled bookings
        cancelled_bookings = all_bookings.filter(status="cancelled").count()

        # Calculate total amount spent
        total_spent = all_bookings.filter(
            status__in=["confirmed", "completed"]
        ).aggregate(total=models.Sum("total_cost"))["total"] or Decimal("0.00")

        # Get favorite academies (academies with most bookings)
        academy_booking_counts = {}
        for booking in all_bookings:
            academy_name = booking.field.academy.name
            academy_booking_counts[academy_name] = (
                academy_booking_counts.get(academy_name, 0) + 1
            )

        # Sort academies by booking count and get top 3
        favorite_academies = sorted(
            academy_booking_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]

        favorite_academies_list = [
            {"academy_name": academy_name, "bookings_count": count}
            for academy_name, count in favorite_academies
        ]

        # Get recent bookings (last 5 bookings)
        recent_bookings = all_bookings.order_by("-created_at")[:5]
        recent_bookings_list = []

        for booking in recent_bookings:
            recent_bookings_list.append(
                {
                    "id": booking.id,
                    "field_name": booking.field.name,
                    "academy_name": booking.field.academy.name,
                    "start_time": booking.start_time.isoformat(),
                    "end_time": booking.end_time.isoformat(),
                    "status": booking.status,
                    "total_cost": str(booking.total_cost),
                    "created_at": booking.created_at.isoformat(),
                }
            )

        # Get booking status distribution
        status_distribution = {}
        for booking in all_bookings:
            status = booking.status
            status_distribution[status] = status_distribution.get(status, 0) + 1

        stats = {
            "user_type": "external_client",
            "user_id": user.id,
            "user_email": user.email,
            "user_name": user.get_full_name(),
            "total_bookings": total_bookings,
            "upcoming_bookings": upcoming_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "pending_bookings": status_distribution.get("pending", 0),
            "confirmed_bookings": status_distribution.get("confirmed", 0),
            "total_spent": str(total_spent),
            "average_booking_cost": str(
                total_spent / total_bookings if total_bookings > 0 else Decimal("0.00")
            ),
            "favorite_academies": favorite_academies_list,
            "recent_bookings": recent_bookings_list,
            "booking_status_distribution": status_distribution,
            "member_since": user.date_joined.isoformat(),
            "last_booking_date": all_bookings.order_by("-created_at")
            .first()
            .created_at.isoformat()
            if all_bookings.exists()
            else None,
        }

        logger.info(f"Retrieved external client dashboard stats for user {user.email}")
        return Response(stats)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint for Docker and load balancers.
    Returns 200 OK if the application is running.
    """
    return Response(
        {
            "status": "healthy",
            "message": "AI Football Platform is running",
            "timestamp": timezone.now().isoformat(),
        },
        status=status.HTTP_200_OK,
    )
