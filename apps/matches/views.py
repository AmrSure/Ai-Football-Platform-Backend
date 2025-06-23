"""Matches views module for the AI Football Platform.

This module contains views for managing matches and match-related
operations with atomic transaction support.
"""

import logging

from django.db import models, transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAcademyAdmin, IsSystemAdmin
from apps.core.views import AcademyScopedViewSet

from .models import Match
from .serializers import MatchSerializer

logger = logging.getLogger(__name__)


class MatchViewSet(AcademyScopedViewSet):
    """
    API endpoints for managing matches with atomic transaction support.

    list: Returns a paginated list of matches
    retrieve: Returns details of a specific match
    create: Creates a new match (academy admin only)
    update: Updates match data (academy admin only)
    partial_update: Partially updates match data (academy admin only)
    destroy: Deletes a match (academy admin only)
    start_match: Start a match
    end_match: End a match
    cancel_match: Cancel a match

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["home_team__name", "away_team__name", "venue__name", "match_type"]
    filterset_fields = [
        "home_team",
        "away_team",
        "venue",
        "match_type",
        "status",
        "is_active",
    ]
    ordering = ["-match_date"]

    def get_permissions(self):
        """
        Academy admins can manage matches in their academy.
        System admins can manage all matches.
        Other users can view matches.
        """
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "start_match",
            "end_match",
            "cancel_match",
        ]:
            self.permission_classes = [IsAuthenticated, IsAcademyAdmin]
        return super().get_permissions()

    def get_queryset(self):
        """
        Return matches based on user permissions and academy scope.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == "system_admin":
            return queryset
        elif hasattr(user, "profile") and hasattr(user.profile, "academy"):
            # Return matches where either home or away team belongs to user's academy
            academy = user.profile.academy
            return queryset.filter(
                models.Q(home_team__academy=academy)
                | models.Q(away_team__academy=academy)
            )

        return queryset.none()

    @swagger_auto_schema(
        operation_summary="List matches",
        operation_description="Returns a paginated list of matches based on user permissions",
        responses={
            200: "List of matches",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve match details",
        operation_description="Returns details of a specific match",
        responses={
            200: "Match details",
            401: "Unauthorized - authentication required",
            404: "Not found - match does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create new match",
        operation_description="Creates a new match (academy admin only)",
        responses={
            201: "Match created successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update match",
        operation_description="Updates match data (academy admin only)",
        responses={
            200: "Match updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this match",
            404: "Not found - match does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update match",
        operation_description="Partially updates match data (academy admin only)",
        responses={
            200: "Match updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this match",
            404: "Not found - match does not exist",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete match",
        operation_description="Deletes a match (academy admin only)",
        responses={
            204: "No content - match deleted successfully",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this match",
            404: "Not found - match does not exist",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Start match",
        operation_description="Starts a scheduled match (academy admin only)",
        responses={
            200: openapi.Response(
                description="Match started successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Updated status"
                        ),
                    },
                ),
            ),
            400: "Bad request - match cannot be started",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - match does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def start_match(self, request, pk=None):
        """
        Start a scheduled match.
        """
        try:
            match = self.get_object()

            if match.status != "scheduled":
                return Response(
                    {"error": f"Cannot start match with status '{match.status}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            match.status = "in_progress"
            match.save()
            logger.info(f"Started match {match.id} by admin {request.user.id}")
            return Response({"status": "in_progress"})
        except Exception as e:
            logger.error(f"Error starting match {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="End match",
        operation_description="Ends an in-progress match (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "home_score": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Home team final score"
                ),
                "away_score": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Away team final score"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Match ended successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Updated status"
                        ),
                        "final_score": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Final score"
                        ),
                    },
                ),
            ),
            400: "Bad request - match cannot be ended",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - match does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def end_match(self, request, pk=None):
        """
        End an in-progress match.
        """
        try:
            match = self.get_object()

            if match.status != "in_progress":
                return Response(
                    {"error": f"Cannot end match with status '{match.status}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            home_score = request.data.get("home_score")
            away_score = request.data.get("away_score")

            if home_score is not None:
                match.home_score = home_score
            if away_score is not None:
                match.away_score = away_score

            match.status = "completed"
            match.save()

            final_score = f"{match.home_score} - {match.away_score}"
            logger.info(
                f"Ended match {match.id} with score {final_score} by admin {request.user.id}"
            )

            return Response({"status": "completed", "final_score": final_score})
        except Exception as e:
            logger.error(f"Error ending match {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Cancel match",
        operation_description="Cancels a scheduled match (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "reason": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Reason for cancellation"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Match cancelled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Updated status"
                        ),
                    },
                ),
            ),
            400: "Bad request - match cannot be cancelled",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - match does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def cancel_match(self, request, pk=None):
        """
        Cancel a scheduled match.
        """
        try:
            match = self.get_object()

            if match.status not in ["scheduled"]:
                return Response(
                    {"error": f"Cannot cancel match with status '{match.status}'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            reason = request.data.get("reason", "")
            if reason:
                match.notes = f"Cancelled: {reason}"

            match.status = "cancelled"
            match.save()
            logger.info(
                f"Cancelled match {match.id} by admin {request.user.id}. Reason: {reason}"
            )
            return Response({"status": "cancelled"})
        except Exception as e:
            logger.error(f"Error cancelling match {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Get match statistics",
        operation_description="Returns statistics for a specific match",
        responses={
            200: openapi.Response(
                description="Match statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_goals": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "home_possession": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "away_possession": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "total_fouls": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - match does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """
        Get statistics for a specific match.
        """
        match = self.get_object()

        # This would typically involve querying detailed match statistics
        # For now, returning basic structure
        stats = {
            "total_goals": (match.home_score or 0) + (match.away_score or 0),
            "home_possession": 50.0,  # Would calculate from actual data
            "away_possession": 50.0,  # Would calculate from actual data
            "total_fouls": 0,  # Would count from match events
        }

        logger.info(f"Retrieved statistics for match {match.id}")
        return Response(stats)
