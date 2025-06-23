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
from .serializers import AcademyAdminProfileSerializer, AcademySerializer

logger = logging.getLogger(__name__)


class AcademyViewSet(BaseModelViewSet):
    """
    API endpoints for managing academies with atomic transaction support.

    list: Returns a paginated list of academies
    retrieve: Returns details of a specific academy
    create: Creates a new academy (system admin only)
    update: Updates academy data (system admin only)
    partial_update: Partially updates academy data (system admin only)
    destroy: Deletes an academy (system admin only)

    All database operations are executed atomically to ensure data consistency.
    """

    queryset = Academy.objects.all()
    serializer_class = AcademySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "name_ar", "email", "phone"]
    filterset_fields = ["is_active"]
    ordering = ["name"]

    def get_permissions(self):
        """
        System admins can perform all operations.
        Other users can only list and retrieve.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsSystemAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List academies",
        operation_description="Returns a paginated list of all academies",
        responses={
            200: "List of academies",
            401: "Unauthorized - authentication required",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve academy details",
        operation_description="Returns details of a specific academy",
        responses={
            200: "Academy details",
            401: "Unauthorized - authentication required",
            404: "Not found - academy does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create new academy",
        operation_description="Creates a new academy (system admin only)",
        responses={
            201: "Academy created successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update academy",
        operation_description="Updates academy data (system admin only)",
        responses={
            200: "Academy updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
            404: "Not found - academy does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update academy",
        operation_description="Partially updates academy data (system admin only)",
        responses={
            200: "Academy updated successfully",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
            404: "Not found - academy does not exist",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete academy",
        operation_description="Deletes an academy (system admin only)",
        responses={
            204: "No content - academy deleted successfully",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
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
