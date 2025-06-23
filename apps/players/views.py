"""Players views module for the AI Football Platform.

This module contains views for managing players, teams, and player-related
operations with atomic transaction support.
"""

import logging

from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAcademyAdmin, IsSystemAdmin
from apps.core.views import AcademyScopedViewSet

from .models import CoachProfile, ParentProfile, PlayerProfile, Team
from .serializers import (
    CoachProfileSerializer,
    ParentProfileSerializer,
    PlayerProfileSerializer,
    TeamSerializer,
)

logger = logging.getLogger(__name__)


class PlayerProfileViewSet(AcademyScopedViewSet):
    """
    API endpoints for managing player profiles with atomic transaction support.

    list: Returns a paginated list of player profiles
    retrieve: Returns details of a specific player profile
    create: Creates a new player profile (academy admin only)
    update: Updates player profile data
    partial_update: Partially updates player profile data
    destroy: Deletes a player profile

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = PlayerProfile.objects.all()
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAuthenticated]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "position",
        "academy__name",
    ]
    filterset_fields = ["academy", "position", "is_active", "team"]
    ordering = ["user__first_name", "user__last_name"]

    def get_permissions(self):
        """
        Academy admins can manage players in their academy.
        System admins can manage all players.
        Players and parents can view player profiles.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAcademyAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List player profiles",
        operation_description="Returns a paginated list of player profiles based on user permissions",
        responses={
            200: "List of player profiles",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve player profile details",
        operation_description="Returns details of a specific player profile",
        responses={
            200: "Player profile details",
            401: "Unauthorized - authentication required",
            404: "Not found - player profile does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create new player profile",
        operation_description="Creates a new player profile (academy admin only)",
        responses={
            201: "Player profile created successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update player profile",
        operation_description="Updates player profile data",
        responses={
            200: "Player profile updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this profile",
            404: "Not found - profile does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get player statistics",
        operation_description="Returns statistics for a specific player",
        responses={
            200: openapi.Response(
                description="Player statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_matches": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_goals": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_assists": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "current_team": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - player does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """
        Get statistics for a specific player.
        """
        player = self.get_object()

        # This would typically involve querying match statistics
        # For now, returning basic structure
        stats = {
            "total_matches": 0,  # player.match_participations.count()
            "total_goals": 0,  # player.goals.count()
            "total_assists": 0,  # player.assists.count()
            "current_team": player.team.name if player.team else None,
        }

        logger.info(f"Retrieved statistics for player {player.id}")
        return Response(stats)


class CoachProfileViewSet(AcademyScopedViewSet):
    """
    API endpoints for managing coach profiles with atomic transaction support.

    list: Returns a paginated list of coach profiles
    retrieve: Returns details of a specific coach profile
    create: Creates a new coach profile (academy admin only)
    update: Updates coach profile data
    partial_update: Partially updates coach profile data
    destroy: Deletes a coach profile

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = CoachProfile.objects.all()
    serializer_class = CoachProfileSerializer
    permission_classes = [IsAuthenticated]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "specialization",
        "academy__name",
    ]
    filterset_fields = ["academy", "specialization", "is_active"]
    ordering = ["user__first_name", "user__last_name"]

    def get_permissions(self):
        """
        Academy admins can manage coaches in their academy.
        System admins can manage all coaches.
        Coaches can view coach profiles.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAcademyAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List coach profiles",
        operation_description="Returns a paginated list of coach profiles based on user permissions",
        responses={
            200: "List of coach profiles",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve coach profile details",
        operation_description="Returns details of a specific coach profile",
        responses={
            200: "Coach profile details",
            401: "Unauthorized - authentication required",
            404: "Not found - coach profile does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get coach's teams",
        operation_description="Returns teams managed by a specific coach",
        responses={
            200: "List of teams managed by the coach",
            401: "Unauthorized - authentication required",
            404: "Not found - coach does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def teams(self, request, pk=None):
        """
        Get teams managed by a specific coach.
        """
        coach = self.get_object()
        teams = coach.teams_coached.filter(is_active=True)

        serializer = TeamSerializer(teams, many=True)
        logger.info(f"Retrieved teams for coach {coach.id}")
        return Response(serializer.data)


class ParentProfileViewSet(AcademyScopedViewSet):
    """
    API endpoints for managing parent profiles with atomic transaction support.

    list: Returns a paginated list of parent profiles
    retrieve: Returns details of a specific parent profile
    create: Creates a new parent profile (academy admin only)
    update: Updates parent profile data
    partial_update: Partially updates parent profile data
    destroy: Deletes a parent profile

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAuthenticated]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "academy__name",
    ]
    filterset_fields = ["academy", "is_active"]
    ordering = ["user__first_name", "user__last_name"]

    def get_permissions(self):
        """
        Academy admins can manage parents in their academy.
        System admins can manage all parents.
        Parents can view parent profiles.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAcademyAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List parent profiles",
        operation_description="Returns a paginated list of parent profiles based on user permissions",
        responses={
            200: "List of parent profiles",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve parent profile details",
        operation_description="Returns details of a specific parent profile",
        responses={
            200: "Parent profile details",
            401: "Unauthorized - authentication required",
            404: "Not found - parent profile does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get parent's children",
        operation_description="Returns children (players) associated with a specific parent",
        responses={
            200: "List of children players",
            401: "Unauthorized - authentication required",
            404: "Not found - parent does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        parent = self.get_object()
        children = parent.children.filter(is_active=True)

        serializer = PlayerProfileSerializer(children, many=True)
        logger.info(f"Retrieved children for parent {parent.id}")
        return Response(serializer.data)


class TeamViewSet(AcademyScopedViewSet):
    """
    API endpoints for managing teams with atomic transaction support.

    list: Returns a paginated list of teams
    retrieve: Returns details of a specific team
    create: Creates a new team (academy admin only)
    update: Updates team data (academy admin only)
    partial_update: Partially updates team data (academy admin only)
    destroy: Deletes a team (academy admin only)
    players: Get players in a team
    add_player: Add a player to the team
    remove_player: Remove a player from the team

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    search_fields = [
        "name",
        "category",
        "academy__name",
        "coach__user__first_name",
        "coach__user__last_name",
    ]
    filterset_fields = ["academy", "category", "is_active", "coach"]
    ordering = ["name"]

    def get_permissions(self):
        """
        Academy admins can manage teams in their academy.
        System admins can manage all teams.
        Coaches and players can view teams.
        """
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "add_player",
            "remove_player",
        ]:
            self.permission_classes = [IsAuthenticated, IsAcademyAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List teams",
        operation_description="Returns a paginated list of teams based on user permissions",
        responses={
            200: "List of teams",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve team details",
        operation_description="Returns details of a specific team",
        responses={
            200: "Team details",
            401: "Unauthorized - authentication required",
            404: "Not found - team does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get team players",
        operation_description="Returns players in a specific team",
        responses={
            200: "List of team players",
            401: "Unauthorized - authentication required",
            404: "Not found - team does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def players(self, request, pk=None):
        """
        Get players in a specific team.
        """
        team = self.get_object()
        players = team.players.filter(is_active=True)

        serializer = PlayerProfileSerializer(players, many=True)
        logger.info(f"Retrieved players for team {team.id}")
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add player to team",
        operation_description="Adds a player to the team (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["player_id"],
            properties={
                "player_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the player to add"
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Player added successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                    },
                ),
            ),
            400: "Bad request - player not found or validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - team does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def add_player(self, request, pk=None):
        """
        Add a player to the team.
        """
        try:
            team = self.get_object()
            player_id = request.data.get("player_id")

            if not player_id:
                return Response(
                    {"error": "player_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                player = PlayerProfile.objects.get(id=player_id, academy=team.academy)
            except PlayerProfile.DoesNotExist:
                return Response(
                    {
                        "error": "Player not found or does not belong to the same academy"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if player.team == team:
                return Response(
                    {"error": "Player is already in this team"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            player.team = team
            player.save()
            logger.info(
                f"Added player {player.id} to team {team.id} by admin {request.user.id}"
            )
            return Response({"status": "Player added to team successfully"})
        except Exception as e:
            logger.error(f"Error adding player to team {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Remove player from team",
        operation_description="Removes a player from the team (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["player_id"],
            properties={
                "player_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the player to remove"
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Player removed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                    },
                ),
            ),
            400: "Bad request - player not found or validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - team does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def remove_player(self, request, pk=None):
        """
        Remove a player from the team.
        """
        try:
            team = self.get_object()
            player_id = request.data.get("player_id")

            if not player_id:
                return Response(
                    {"error": "player_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                player = PlayerProfile.objects.get(id=player_id, team=team)
            except PlayerProfile.DoesNotExist:
                return Response(
                    {"error": "Player not found in this team"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            player.team = None
            player.save()
            logger.info(
                f"Removed player {player.id} from team {team.id} by admin {request.user.id}"
            )
            return Response({"status": "Player removed from team successfully"})
        except Exception as e:
            logger.error(f"Error removing player from team {pk}: {str(e)}")
            raise
