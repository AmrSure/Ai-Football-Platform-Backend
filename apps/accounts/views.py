import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.core.permissions import IsAcademyAdmin, IsAcademyAdminForUser, IsSystemAdmin
from apps.core.serializers import BaseUserSerializer
from apps.core.views import BaseModelViewSet

from .serializers import (
    AcademyUserRegistrationSerializer,
    AcademyUserUpdateSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    UserRegistrationSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Email-based JWT Token Authentication Endpoint with Profile Information.

    Takes user email and password and returns an access and refresh JSON web token pair
    along with comprehensive user information including profile data using appropriate
    nested serializers based on user type.

    **Authentication Method**: Email + Password

    **Request Format**:
    ```json
    {
      "username": "user@example.com",  // Field name is "username" but expects email address
      "password": "your_password"
    }
    ```

    **Response Format for Parent User**:
    ```json
    {
      "access": "jwt_access_token",
      "refresh": "jwt_refresh_token",
      "user_id": 1,
      "email": "parent@example.com",
      "user_type": "parent",
      "first_name": "John",
      "last_name": "Doe",
      "profile": {
        "id": 1,
        "user": {
          "id": 1,
          "email": "parent@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "relationship": "father",
        "bio": "Parent bio information",
        "date_of_birth": "1980-01-01",
        "children": [
          {
            "id": 2,
            "user": {
              "id": 2,
              "email": "child@example.com",
              "first_name": "Jane",
              "last_name": "Doe"
            },
            "jersey_number": "10",
            "position": "midfielder"
          }
        ],
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    }
    ```

    **Profile Serializers by User Type**:
    - **parent**: Uses `ParentProfileNestedSerializer` with children information
    - **player**: Uses `PlayerProfileNestedSerializer` with parents and teams
    - **coach**: Uses `CoachProfileNestedSerializer` with specialization details
    - **academy_admin**: Uses `AcademyAdminProfileNestedSerializer`
    - **external_client/system_admin**: Basic profile information

    **Features**:
    - Email-based authentication (case-insensitive)
    - Returns extended user information and complete profile data
    - Uses appropriate nested serializers based on user type
    - Compatible with standard JWT token refresh flow
    - Safe error handling - authentication won't fail if profile data is unavailable
    """

    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for external client self-registration with atomic transaction support.

    Only allows registration with user_type='external_client'.
    Other user types must be registered by an academy admin.
    All database operations are executed atomically to ensure data consistency.

    Required fields:
    - email: Valid email address (used for login)
    - password: Password meeting complexity requirements
    - password_confirm: Must match password
    - first_name: User's first name
    - last_name: User's last_name
    - user_type: Must be 'external_client'

    Optional fields:
    - phone: Contact phone number
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create user and profile with atomic transaction.

        Ensures that both user creation and profile creation are
        executed atomically to maintain data consistency.
        """
        try:
            user = serializer.save()
            logger.info(f"Successfully created external client user: {user.email}")
        except Exception as e:
            logger.error(f"Error creating external client user: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Register a new external client user",
        operation_description="Creates a new user account with user_type='external_client'",
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "user_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "phone": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad request - validation errors",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AcademyUserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for academy admins to register coaches, players, and parents with atomic transaction support.

    Only academy admins can access this endpoint. Only allows registration of users with
    user_type in ['coach', 'player', 'parent'].
    All database operations are executed atomically to ensure data consistency.

    Required fields:
    - email: Valid email address (used for login)
    - password: Password meeting complexity requirements
    - user_type: One of 'coach', 'player', or 'parent'
    - academy_id: ID of the academy to associate the user with

    Optional fields:
    - first_name: User's first name
    - last_name: User's last name
    - phone: Contact phone number
    """

    queryset = User.objects.all()
    serializer_class = AcademyUserRegistrationSerializer
    permission_classes = [IsAuthenticated, IsAcademyAdmin]

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create user and profile with atomic transaction.

        Ensures that user creation, profile creation, and academy
        association are executed atomically to maintain data consistency.
        """
        try:
            user = serializer.save()
            logger.info(
                f"Successfully created academy user: {user.email} of type: {user.user_type}"
            )
        except Exception as e:
            logger.error(f"Error creating academy user: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Register a new academy user",
        operation_description="Creates a new user account with user_type in ['coach', 'player', 'parent']",
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "user_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "phone": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout with atomic transaction support.

    Blacklists the provided refresh token to prevent further use.
    Requires authentication. Token blacklisting is done atomically.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Logout user",
        operation_description="Blacklists the refresh token to prevent further use",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="JWT refresh token"
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        )
                    },
                ),
            ),
            400: "Bad request - invalid token",
            401: "Unauthorized - authentication required",
        },
    )
    @transaction.atomic
    def post(self, request):
        """
        Logout user by blacklisting refresh token.

        Uses atomic transaction to ensure token blacklisting
        is completed successfully or rolled back on error.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User {request.user.id} logged out successfully")
            return Response(
                {"message": "Successfully logged out"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating the current user's profile.

    GET: Returns the user's profile data
    PUT/PATCH: Updates the user's profile data

    The profile model returned depends on the user's type (coach, player, parent, etc.)
    """

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def get_serializer_class(self):
        return ProfileSerializer

    @swagger_auto_schema(
        operation_summary="Get current user's profile",
        operation_description="Returns the profile data for the authenticated user",
        responses={
            200: "User profile data",
            401: "Unauthorized - authentication required",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update current user's profile",
        operation_description="Updates the profile data for the authenticated user",
        responses={
            200: "Updated profile data",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update current user's profile",
        operation_description="Partially updates the profile data for the authenticated user",
        responses={
            200: "Updated profile data",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for changing the current user's password with atomic transaction support.

    Requires the old password for verification and a new password that meets
    complexity requirements. All operations are executed atomically.
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_summary="Change user password",
        operation_description="Changes the password for the authenticated user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["old_password", "new_password", "new_password_confirm"],
            properties={
                "old_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Current password"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New password"
                ),
                "new_password_confirm": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Confirmation of new password"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Password updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        )
                    },
                ),
            ),
            400: "Bad request - validation errors or wrong password",
            401: "Unauthorized - authentication required",
        },
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update user password with atomic transaction.

        Ensures password change is executed atomically to
        maintain data consistency and security.
        """
        try:
            user = self.get_object()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Check old password
                if not user.check_password(serializer.data.get("old_password")):
                    return Response(
                        {"old_password": "Wrong password."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Set new password
                user.set_password(serializer.data.get("new_password"))
                user.save()
                logger.info(f"Password changed for user {user.id}")

                return Response(
                    {"message": "Password updated successfully"},
                    status=status.HTTP_200_OK,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(
                f"Error changing password for user {request.user.id}: {str(e)}"
            )
            raise


class UserViewSet(BaseModelViewSet):
    """
    API endpoints for system administrators to manage all users in the system.

    list: Returns a paginated list of all users
    retrieve: Returns details of a specific user
    create: Creates a new user
    update: Updates a user's data
    partial_update: Partially updates a user's data
    destroy: Deletes a user

    Only system administrators can create, update, or delete users through this endpoint.
    """

    queryset = User.objects.all()
    serializer_class = BaseUserSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["email", "first_name", "last_name"]
    filterset_fields = ["user_type", "is_active"]
    ordering = ["-date_joined"]

    def get_permissions(self):
        # Only system admins can access this viewset
        self.permission_classes = [IsSystemAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description="Returns a paginated list of all users in the system",
        responses={200: "List of users", 401: "Unauthorized - authentication required"},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a specific user",
        operation_description="Returns details of a specific user by ID",
        responses={
            200: "User details",
            401: "Unauthorized - authentication required",
            404: "Not found - user does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        operation_description="Creates a new user (system admin only)",
        responses={
            201: "Created user details",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a user",
        operation_description="Updates a user's data (system admin only)",
        responses={
            200: "Updated user details",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
            404: "Not found - user does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a user",
        operation_description="Partially updates a user's data (system admin only)",
        responses={
            200: "Updated user details",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
            404: "Not found - user does not exist",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a user",
        operation_description="Deletes a user (system admin only)",
        responses={
            204: "No content - user deleted successfully",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
            404: "Not found - user does not exist",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Activate a user",
        operation_description="Sets a user's is_active flag to True (system admin only)",
        responses={
            200: openapi.Response(
                description="User activated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Status message"
                        )
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
            404: "Not found - user does not exist",
        },
    )
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "User activated"})

    @swagger_auto_schema(
        operation_summary="Deactivate a user",
        operation_description="Sets a user's is_active flag to False (system admin only)",
        responses={
            200: openapi.Response(
                description="User deactivated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Status message"
                        )
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not a system admin",
            404: "Not found - user does not exist",
        },
    )
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"status": "User deactivated"})


class AcademyUserViewSet(BaseModelViewSet):
    """
    API endpoints for academy administrators to manage users in their academy with atomic transaction support.

    Allows academy admins to list, create, update, and delete coach, player, and parent users
    that belong to their academy. All database operations are executed atomically.

    list: Returns a paginated list of users in the admin's academy
    retrieve: Returns details of a specific user in the admin's academy
    update: Updates a user's data
    partial_update: Partially updates a user's data
    destroy: Deletes a user from the academy
    activate: Sets a user's is_active flag to True
    deactivate: Sets a user's is_active flag to False
    reset_password: Resets a user's password

    Only academy administrators can access these endpoints, and they can only
    manage users that belong to their own academy.
    """

    permission_classes = [IsAuthenticated, IsAcademyAdmin]
    search_fields = ["email", "first_name", "last_name"]
    filterset_fields = ["user_type", "is_active"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action in ["update", "partial_update"]:
            return AcademyUserUpdateSerializer
        return BaseUserSerializer

    def get_queryset(self):
        """
        Return only users that belong to the admin's academy.
        """
        if not hasattr(self.request.user, "profile") or not hasattr(
            self.request.user.profile, "academy"
        ):
            return User.objects.none()

        academy = self.request.user.profile.academy
        if academy is None:
            return User.objects.none()

        # Get all users with profiles in this academy
        # Import the profile models to check academy relationships
        from apps.academies.models import CoachProfile, ParentProfile, PlayerProfile

        # Get users with academy-related profiles
        coach_users = User.objects.filter(
            user_type="coach", profile__in=CoachProfile.objects.filter(academy=academy)
        )
        player_users = User.objects.filter(
            user_type="player",
            profile__in=PlayerProfile.objects.filter(academy=academy),
        )
        parent_users = User.objects.filter(
            user_type="parent",
            profile__in=ParentProfile.objects.filter(children__academy=academy),
        )

        # Combine all querysets
        return (coach_users | player_users | parent_users).distinct()

    def get_permissions(self):
        """
        Use IsAcademyAdminForUser permission for object-level actions.
        """
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAcademyAdminForUser]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List academy users",
        operation_description="Returns a paginated list of users in the admin's academy",
        responses={
            200: "List of users",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not an academy admin",
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve an academy user",
        operation_description="Returns details of a specific user in the admin's academy",
        responses={
            200: "User details",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not in admin's academy",
            404: "Not found - user does not exist",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an academy user",
        operation_description="Updates a user's data in the admin's academy",
        responses={
            200: "Updated user details",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not in admin's academy",
            404: "Not found - user does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update an academy user",
        operation_description="Partially updates a user's data in the admin's academy",
        responses={
            200: "Updated user details",
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not in admin's academy",
            404: "Not found - user does not exist",
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete an academy user",
        operation_description="Deletes a user from the admin's academy",
        responses={
            204: "No content - user deleted successfully",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not in admin's academy",
            404: "Not found - user does not exist",
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Activate an academy user",
        operation_description="Sets a user's is_active flag to True",
        responses={
            200: openapi.Response(
                description="User activated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Status message"
                        )
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not in admin's academy",
            404: "Not found - user does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """
        Activate a user in the admin's academy with atomic transaction.
        """
        try:
            user = self.get_object()
            user.is_active = True
            user.save()
            logger.info(f"Activated user {user.id} by admin {request.user.id}")
            return Response({"status": "User activated"})
        except Exception as e:
            logger.error(f"Error activating user {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Deactivate an academy user",
        operation_description="Sets a user's is_active flag to False",
        responses={
            200: openapi.Response(
                description="User deactivated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Status message"
                        )
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not in admin's academy",
            404: "Not found - user does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user in the admin's academy with atomic transaction.
        """
        try:
            user = self.get_object()
            user.is_active = False
            user.save()
            logger.info(f"Deactivated user {user.id} by admin {request.user.id}")
            return Response({"status": "User deactivated"})
        except Exception as e:
            logger.error(f"Error deactivating user {pk}: {str(e)}")
            raise

    @swagger_auto_schema(
        operation_summary="Reset an academy user's password",
        operation_description="Resets the password for a user in the admin's academy",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["new_password"],
            properties={
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New password"
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Password reset successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Status message"
                        )
                    },
                ),
            ),
            400: "Bad request - validation errors",
            401: "Unauthorized - authentication required",
            403: "Forbidden - user is not in admin's academy",
            404: "Not found - user does not exist",
        },
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        """
        Reset password for a user in the admin's academy with atomic transaction.
        """
        try:
            user = self.get_object()
            new_password = request.data.get("new_password")

            if not new_password:
                return Response(
                    {"error": "New password is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validate_password(new_password, user)
            user.set_password(new_password)
            user.save()
            logger.info(f"Reset password for user {user.id} by admin {request.user.id}")
            return Response({"status": "Password reset successful"})
        except Exception as e:
            logger.error(f"Error resetting password for user {pk}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
