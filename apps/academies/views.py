"""Academy views module for the AI Football Platform.

This module contains views for managing academies, academy profiles, and
academy-related operations with atomic transaction support.
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
from apps.core.views import BaseModelViewSet

from .models import Academy, AcademyAdminProfile
from .serializers import (
    AcademyAdminProfileSerializer,
    AcademyDetailSerializer,
    AcademySerializer,
)

logger = logging.getLogger(__name__)


class AcademyViewSet(BaseModelViewSet):
    """
    API endpoints for managing academies with atomic transaction support.

    Permissions:
    - System administrators: Can perform all operations (CRUD)
    - Academy users: Can only view academies (list/retrieve their own academy)
    - External clients: Cannot access academy endpoints

    list: Returns a paginated list of academies (filtered by user permissions)
    retrieve: Returns details of a specific academy
    create: Creates a new academy (SYSTEM ADMIN ONLY)
    update: Updates academy data (SYSTEM ADMIN ONLY)
    partial_update: Partially updates academy data (SYSTEM ADMIN ONLY)
    destroy: Deletes an academy (SYSTEM ADMIN ONLY)

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = Academy.objects.all()
    serializer_class = AcademySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "name_ar", "email", "phone"]
    filterset_fields = ["is_active"]
    ordering = ["name"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        Use detailed serializer for retrieve to include all nested objects.
        """
        if self.action == "retrieve":
            return AcademyDetailSerializer
        return AcademySerializer

    def get_queryset(self):
        """
        Return academies based on user permissions.
        System admins can see all academies.
        Other users can only see academies they have access to.
        """
        queryset = super().get_queryset()
        user = self.request.user

        # Add prefetch_related for detailed retrieval
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "admins__user",
                "coaches__user",
                "players__user",
                "players__parents__user",
                "players__teams",
                "fields__bookings__booked_by",
            ).select_related()

        if user.user_type == "system_admin":
            # System admins can see all academies
            return queryset
        elif hasattr(user, "profile") and hasattr(user.profile, "academy"):
            # Academy users can only see their own academy
            return queryset.filter(id=user.profile.academy.id)
        else:
            # External clients and users without academy profiles see no academies
            return queryset.none()

    def get_permissions(self):
        """
        System admins can perform all operations.
        Other users can only list and retrieve.
        Only system administrators can create, update, or delete academies.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsSystemAdmin]
        else:
            # For list and retrieve operations, only require authentication
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List academies",
        operation_description="Returns a paginated list of academies based on user permissions. System admins see all academies, academy users see only their academy.",
        responses={
            200: "List of academies",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve academy details with all nested objects",
        operation_description="Returns comprehensive details of a specific academy including all related entities: admins, coaches, players, teams, fields, and statistics. This endpoint provides complete academy information with all nested relationships.",
        responses={
            200: openapi.Response(
                description="Comprehensive academy details with all nested objects",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "name_ar": openapi.Schema(type=openapi.TYPE_STRING),
                        "description": openapi.Schema(type=openapi.TYPE_STRING),
                        "logo": openapi.Schema(type=openapi.TYPE_STRING),
                        "address": openapi.Schema(type=openapi.TYPE_STRING),
                        "phone": openapi.Schema(type=openapi.TYPE_STRING),
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "website": openapi.Schema(type=openapi.TYPE_STRING),
                        "established_date": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                        ),
                        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                        "updated_at": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                        "admins": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "user": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "position": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "bio": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                        ),
                        "coaches": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "user": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "specialization": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "experience_years": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                        ),
                        "players": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "user": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "jersey_number": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "position": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "parents": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                    ),
                                    "teams": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                    ),
                                },
                            ),
                        ),
                        "teams": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "age_group": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "coach": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "players": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                    ),
                                    "total_players": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                },
                            ),
                        ),
                        "fields": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "field_type": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "capacity": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "upcoming_bookings": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_OBJECT),
                                    ),
                                },
                            ),
                        ),
                        "statistics": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "total_admins": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "total_coaches": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "total_players": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "total_parents": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "total_teams": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "total_fields": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "coaches_by_specialization": openapi.Schema(
                                    type=openapi.TYPE_OBJECT
                                ),
                                "players_by_position": openapi.Schema(
                                    type=openapi.TYPE_OBJECT
                                ),
                                "teams_by_age_group": openapi.Schema(
                                    type=openapi.TYPE_OBJECT
                                ),
                                "fields_by_type": openapi.Schema(
                                    type=openapi.TYPE_OBJECT
                                ),
                            },
                        ),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - academy does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve academy with all nested objects and comprehensive information.
        """
        try:
            response = super().retrieve(request, *args, **kwargs)
            academy_id = kwargs.get("pk")
            logger.info(
                f"Retrieved comprehensive academy details for academy {academy_id} "
                f"by user {request.user.email}"
            )
            return response
        except Exception as e:
            logger.error(f"Error retrieving academy details: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Create new academy",
        operation_description="Creates a new academy. Only system administrators can create academies.",
        responses={
            201: "Academy created successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - only system administrators can create academies",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update academy",
        operation_description="Updates academy data. Only system administrators can update academies.",
        responses={
            200: "Academy updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - only system administrators can update academies",
            404: "Not found - academy does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update academy",
        operation_description="Partially updates academy data. Only system administrators can update academies.",
        responses={
            200: "Academy updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - only system administrators can update academies",
            404: "Not found - academy does not exist",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete academy",
        operation_description="Deletes an academy. Only system administrators can delete academies.",
        responses={
            204: "No content - academy deleted successfully",
            401: "Unauthorized - authentication required",
            403: "Forbidden - only system administrators can delete academies",
            404: "Not found - academy does not exist",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get academy statistics",
        operation_description="Returns statistics for a specific academy",
        responses={
            200: openapi.Response(
                description="Academy statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_coaches": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_players": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_parents": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_teams": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "total_fields": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            404: "Not found - academy does not exist",
        },
    )
    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """
        Get statistics for a specific academy.
        """
        academy = self.get_object()

        stats = {
            "total_coaches": academy.coaches.filter(is_active=True).count(),
            "total_players": academy.players.filter(is_active=True).count(),
            "total_parents": academy.parents.filter(is_active=True).count(),
            "total_teams": getattr(academy, "teams", academy.team_set)
            .filter(is_active=True)
            .count(),
            "total_fields": academy.fields.filter(is_active=True).count(),
        }

        logger.info(f"Retrieved statistics for academy {academy.id}")
        return Response(stats)


class AcademyAdminProfileViewSet(BaseModelViewSet):
    """
    API endpoints for managing academy admin profiles with atomic transaction support.

    list: Returns a paginated list of academy admin profiles
    retrieve: Returns details of a specific admin profile
    create: Creates a new admin profile (system admin only)
    update: Updates admin profile data
    partial_update: Partially updates admin profile data
    destroy: Deletes an admin profile

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = AcademyAdminProfile.objects.all()
    serializer_class = AcademyAdminProfileSerializer
    permission_classes = [IsAuthenticated, IsAcademyAdmin]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "academy__name",
    ]
    filterset_fields = ["academy", "is_active"]
    ordering = ["-created_at"]

    def get_permissions(self):
        """
        System admins can perform all operations.
        Academy admins can only manage profiles in their academy.
        """
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, IsSystemAdmin]
        return super().get_permissions()

    def get_queryset(self):
        """
        Return profiles based on user permissions.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.user_type == "system_admin":
            return queryset
        elif hasattr(user, "profile") and hasattr(user.profile, "academy"):
            return queryset.filter(academy=user.profile.academy)

        return queryset.none()

    @swagger_auto_schema(
        operation_summary="List academy admin profiles",
        operation_description="Returns a paginated list of academy admin profiles",
        responses={
            200: "List of admin profiles",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve admin profile details",
        operation_description="Returns details of a specific admin profile",
        responses={
            200: "Admin profile details",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this profile",
            404: "Not found - profile does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create new admin profile",
        operation_description="Creates a new academy admin profile (system admin only)",
        responses={
            201: "Admin profile created successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update admin profile",
        operation_description="Updates admin profile data",
        responses={
            200: "Admin profile updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this profile",
            404: "Not found - profile does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update admin profile",
        operation_description="Partially updates admin profile data",
        responses={
            200: "Admin profile updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this profile",
            404: "Not found - profile does not exist",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete admin profile",
        operation_description="Deletes an academy admin profile",
        responses={
            204: "No content - profile deleted successfully",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user does not have access to this profile",
            404: "Not found - profile does not exist",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
