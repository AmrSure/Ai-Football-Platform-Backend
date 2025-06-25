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

from apps.academies.models import CoachProfile, ParentProfile, PlayerProfile
from apps.core.permissions import IsAcademyAdmin, IsSystemAdmin
from apps.core.views import AcademyScopedViewSet

from .models import Team
from .serializers import (
    CoachProfileSerializer,
    ParentProfileSerializer,
    PlayerProfileSerializer,
    TeamDetailSerializer,
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
    filterset_fields = ["academy", "position", "is_active", "teams"]
    ordering = ["user__first_name", "user__last_name"]

    def get_permissions(self):
        """
        Academy admins can manage players in their academy.
        System admins can manage all players.
        Players and parents can view player profiles.
        """
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "add_parent",
            "remove_parent",
        ]:
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

    @swagger_auto_schema(
        operation_summary="Get player's parents",
        operation_description="Returns parents associated with a specific player",
        responses={
            200: "List of player's parents",
            401: "Unauthorized - authentication required",
            404: "Not found - player does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def parents(self, request, pk=None):
        """
        Get parents for a specific player.
        """
        player = self.get_object()
        parents = player.parents.filter(is_active=True)

        serializer = ParentProfileSerializer(parents, many=True)
        logger.info(f"Retrieved parents for player {player.id}")
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add parent to player",
        operation_description="Associates a parent to the player (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["parent_id"],
            properties={
                "parent_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the parent to add"
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Parent added successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "player_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "parent_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad request - parent not found or validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - player does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def add_parent(self, request, pk=None):
        """
        Add a parent to the player.
        """
        try:
            player = self.get_object()
            parent_id = request.data.get("parent_id")

            if not parent_id:
                return Response(
                    {"error": "parent_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                parent = ParentProfile.objects.get(id=parent_id, is_active=True)
            except ParentProfile.DoesNotExist:
                return Response(
                    {"error": "Parent not found or is inactive"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if parent is already associated with this player
            if player.parents.filter(id=parent.id).exists():
                return Response(
                    {"error": "Parent is already associated with this player"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate academy relationship
            parent_academy = None
            existing_children = parent.children.filter(academy__isnull=False).first()
            if existing_children:
                parent_academy = existing_children.academy

            if parent_academy and player.academy and parent_academy != player.academy:
                return Response(
                    {
                        "error": f"Player's academy ({player.academy.name}) does not match parent's children academy ({parent_academy.name})"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Add the parent (use the parent's children relationship)
            parent.children.add(player)
            logger.info(
                f"Added parent {parent.id} to player {player.id} by admin {request.user.id}"
            )

            return Response(
                {
                    "status": "Parent added to player successfully",
                    "player_id": player.id,
                    "parent_id": parent.id,
                }
            )
        except Exception as e:
            logger.error(f"Error adding parent to player {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Remove parent from player",
        operation_description="Removes a parent from the player (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["parent_id"],
            properties={
                "parent_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID of the parent to remove"
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Parent removed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "player_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "parent_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad request - parent not found or validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - player does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def remove_parent(self, request, pk=None):
        """
        Remove a parent from the player.
        """
        try:
            player = self.get_object()
            parent_id = request.data.get("parent_id")

            if not parent_id:
                return Response(
                    {"error": "parent_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                parent = ParentProfile.objects.get(id=parent_id)
            except ParentProfile.DoesNotExist:
                return Response(
                    {"error": "Parent not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if parent is actually associated with this player
            if not player.parents.filter(id=parent.id).exists():
                return Response(
                    {"error": "Parent is not associated with this player"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Remove the parent (use the parent's children relationship)
            parent.children.remove(player)
            logger.info(
                f"Removed parent {parent.id} from player {player.id} by admin {request.user.id}"
            )

            return Response(
                {
                    "status": "Parent removed from player successfully",
                    "player_id": player.id,
                    "parent_id": parent.id,
                }
            )
        except Exception as e:
            logger.error(f"Error removing parent from player {pk}: {str(e)}")
            raise


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
        "children__academy__name",
    ]
    filterset_fields = ["children__academy", "is_active"]
    ordering = ["user__first_name", "user__last_name"]

    def get_queryset(self):
        """
        Override to handle academy filtering for parent profiles.
        Parents don't have direct academy relationships - they're linked through their children.
        """
        from apps.core.views import BaseModelViewSet

        queryset = BaseModelViewSet.get_queryset(
            self
        )  # Skip AcademyScopedViewSet filtering
        user = self.request.user

        # Apply academy-specific filtering for parents
        if user.user_type == "system_admin":
            return queryset
        elif hasattr(user, "profile") and hasattr(user.profile, "academy"):
            # For now, show all parents in the system (can be restricted later in production)
            # This allows academy admins to manage parent-child relationships
            return queryset

        return queryset.none()

    def get_permissions(self):
        """
        Academy admins can manage parents in their academy.
        System admins can manage all parents.
        Parents can view parent profiles.
        """
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "add_child",
            "remove_child",
            "set_children",
        ]:
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

    @swagger_auto_schema(
        operation_summary="Add child to parent",
        operation_description="Associates a player as a child of the parent (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["player_id"],
            properties={
                "player_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the player to add as child",
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Child added successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "parent_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "child_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad request - player not found or validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - parent does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def add_child(self, request, pk=None):
        """
        Add a child (player) to the parent.
        """
        try:
            parent = self.get_object()
            player_id = request.data.get("player_id")

            if not player_id:
                return Response(
                    {"error": "player_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                player = PlayerProfile.objects.get(id=player_id, is_active=True)
            except PlayerProfile.DoesNotExist:
                return Response(
                    {"error": "Player not found or is inactive"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if player is already a child of this parent
            if parent.children.filter(id=player.id).exists():
                return Response(
                    {"error": "Player is already a child of this parent"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate academy relationship if both have academies
            parent_academy = None
            existing_children = parent.children.filter(academy__isnull=False).first()
            if existing_children:
                parent_academy = existing_children.academy

            if parent_academy and player.academy and parent_academy != player.academy:
                return Response(
                    {
                        "error": f"Player's academy ({player.academy.name}) does not match parent's children academy ({parent_academy.name})"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Add the child
            parent.children.add(player)
            logger.info(
                f"Added player {player.id} as child to parent {parent.id} by admin {request.user.id}"
            )

            return Response(
                {
                    "status": "Child added to parent successfully",
                    "parent_id": parent.id,
                    "child_id": player.id,
                }
            )
        except Exception as e:
            logger.error(f"Error adding child to parent {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Remove child from parent",
        operation_description="Removes a player as a child of the parent (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["player_id"],
            properties={
                "player_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the player to remove as child",
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Child removed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "parent_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "child_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad request - player not found or validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - parent does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def remove_child(self, request, pk=None):
        """
        Remove a child (player) from the parent.
        """
        try:
            parent = self.get_object()
            player_id = request.data.get("player_id")

            if not player_id:
                return Response(
                    {"error": "player_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                player = PlayerProfile.objects.get(id=player_id)
            except PlayerProfile.DoesNotExist:
                return Response(
                    {"error": "Player not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if player is actually a child of this parent
            if not parent.children.filter(id=player.id).exists():
                return Response(
                    {"error": "Player is not a child of this parent"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Remove the child
            parent.children.remove(player)
            logger.info(
                f"Removed player {player.id} as child from parent {parent.id} by admin {request.user.id}"
            )

            return Response(
                {
                    "status": "Child removed from parent successfully",
                    "parent_id": parent.id,
                    "child_id": player.id,
                }
            )
        except Exception as e:
            logger.error(f"Error removing child from parent {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Set parent's children",
        operation_description="Sets the complete list of children for a parent, replacing existing relationships (academy admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["player_ids"],
            properties={
                "player_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description="List of player IDs to set as children",
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Children set successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                        "parent_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "children_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
            404: "Not found - parent does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def set_children(self, request, pk=None):
        """
        Set the complete list of children for a parent.
        This replaces all existing parent-child relationships for this parent.
        """
        try:
            parent = self.get_object()
            player_ids = request.data.get("player_ids", [])

            if not isinstance(player_ids, list):
                return Response(
                    {"error": "player_ids must be a list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate all player IDs exist and are active
            players = []
            for player_id in player_ids:
                try:
                    player = PlayerProfile.objects.get(id=player_id, is_active=True)
                    players.append(player)
                except PlayerProfile.DoesNotExist:
                    return Response(
                        {
                            "error": f"Player with ID {player_id} not found or is inactive"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Validate academy relationships
            if players:
                academy_set = set(
                    player.academy for player in players if player.academy
                )
                if len(academy_set) > 1:
                    return Response(
                        {"error": "All children must belong to the same academy"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Set the children (this will clear existing relationships and set new ones)
            parent.children.set(players)
            logger.info(
                f"Set {len(players)} children for parent {parent.id} by admin {request.user.id}"
            )

            return Response(
                {
                    "status": "Children set successfully",
                    "parent_id": parent.id,
                    "children_count": len(players),
                }
            )
        except Exception as e:
            logger.error(f"Error setting children for parent {pk}: {str(e)}")
            raise


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

    def get_serializer_class(self):
        """Use TeamDetailSerializer for detail views."""
        if self.action == "retrieve":
            return TeamDetailSerializer
        return TeamSerializer

    search_fields = [
        "name",
        "age_group",
        "academy__name",
        "coach__user__first_name",
        "coach__user__last_name",
    ]
    filterset_fields = ["academy", "age_group", "is_active", "coach"]
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
        operation_summary="Get team statistics",
        operation_description="Returns statistics for a specific team",
        responses={
            200: openapi.Response(
                description="Team statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_players": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "active_players": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "team_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - team does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """
        Get statistics for a specific team.
        """
        team = self.get_object()
        stats = {
            "team_id": team.id,
            "total_players": team.players.count(),
            "active_players": team.players.filter(is_active=True).count(),
            "team_name": team.name,
            "age_group": team.age_group,
        }
        logger.info(f"Retrieved statistics for team {team.id}")
        return Response(stats)

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

            if team in player.teams.all():
                return Response(
                    {"error": "Player is already in this team"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            player.teams.add(team)
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
                player = PlayerProfile.objects.get(id=player_id, teams=team)
            except PlayerProfile.DoesNotExist:
                return Response(
                    {"error": "Player not found in this team"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            player.teams.remove(team)
            logger.info(
                f"Removed player {player.id} from team {team.id} by admin {request.user.id}"
            )
            return Response({"status": "Player removed from team successfully"})
        except Exception as e:
            logger.error(f"Error removing player from team {pk}: {str(e)}")
            raise
