from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.academies.models import (
    AcademyAdminProfile,
    CoachProfile,
    ExternalClientProfile,
    ParentProfile,
    PlayerProfile,
)
from apps.academies.serializers import (
    AcademyAdminProfileNestedSerializer,
    CoachProfileNestedSerializer,
    ParentProfileNestedSerializer,
    PlayerProfileNestedSerializer,
)
from apps.core.serializers import BaseUserSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that extends the default TokenObtainPairSerializer.

    Adds additional user information and profile data to the token response,
    using appropriate nested serializers based on user type.

    Fields:
    - email: User's email for authentication
    - password: User's password for authentication

    Returns:
    - access: JWT access token
    - refresh: JWT refresh token
    - user_id: ID of the authenticated user
    - email: Email of the authenticated user
    - user_type: Type of the authenticated user (system_admin, academy_admin, coach, etc.)
    - first_name: First name of the authenticated user
    - last_name: Last name of the authenticated user
    - profile: Complete profile information using appropriate nested serializer
    """

    def validate(self, attrs):
        # Get the token data from the parent class
        data = super().validate(attrs)

        # Add custom claims
        user = self.user

        # Get profile data using appropriate serializer
        profile_data = self._get_profile_data(user)

        data.update(
            {
                "user_id": user.id,
                "email": user.email,
                "user_type": user.user_type,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile": profile_data,
            }
        )

        return data

    def _get_profile_data(self, user):
        """
        Get profile data using appropriate nested serializer based on user type.
        """
        try:
            if not hasattr(user, "profile") or not user.profile:
                return None

            profile = user.profile

            # Map user types to their respective nested serializers
            profile_serializers = {
                "parent": ParentProfileNestedSerializer,
                "player": PlayerProfileNestedSerializer,
                "coach": CoachProfileNestedSerializer,
                "academy_admin": AcademyAdminProfileNestedSerializer,
            }

            # Get the appropriate serializer for the user type
            serializer_class = profile_serializers.get(user.user_type)

            if serializer_class:
                serializer = serializer_class(profile)
                return serializer.data
            else:
                # For user types without specific nested serializers (like external_client, system_admin)
                # Return basic profile information
                return {
                    "id": profile.id,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "full_name": user.get_full_name(),
                        "user_type": user.user_type,
                    },
                    "bio": getattr(profile, "bio", ""),
                    "date_of_birth": getattr(profile, "date_of_birth", None),
                    "is_active": getattr(profile, "is_active", True),
                    "created_at": getattr(profile, "created_at", None),
                }

        except Exception as e:
            # Log the error but don't fail authentication
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Error getting profile data for user {user.id}: {str(e)}")
            return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for external client self-registration.

    Only allows registration with user_type='external_client'.
    Validates that passwords match and creates appropriate user profile.

    Fields:
    - email: Valid email address (used for login)
    - password: Password meeting complexity requirements
    - password_confirm: Must match password
    - first_name: User's first name
    - last_name: User's last name
    - user_type: Must be 'external_client'
    - phone: Contact phone number (optional)
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "user_type",
            "phone",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Password fields didn't match.")

        # Only allow external_client to self-register
        if attrs.get("user_type") != "external_client":
            raise serializers.ValidationError(
                {
                    "user_type": "Only external clients can self-register. Other user types must be registered by an academy admin."
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create appropriate profile based on user type
        self.create_user_profile(user)

        return user

    def create_user_profile(self, user):
        """Create user profile based on user type"""
        profile_classes = {
            "academy_admin": AcademyAdminProfile,
            "coach": CoachProfile,
            "player": PlayerProfile,
            "parent": ParentProfile,
            "external_client": ExternalClientProfile,
        }

        profile_class = profile_classes.get(user.user_type)
        if profile_class:
            profile_class.objects.create(user=user)


class AcademyUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for academy admin to register coaches, players, and parents.

    Only allows registration of users with user_type in ['coach', 'player', 'parent'].
    Creates appropriate user profile and associates it with the specified academy.

    Fields:
    - email: Valid email address (used for login)
    - password: Password meeting complexity requirements
    - user_type: One of 'coach', 'player', or 'parent'
    - academy_id: ID of the academy to associate the user with
    - first_name: User's first name (optional)
    - last_name: User's last name (optional)
    - phone: Contact phone number (optional)
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    academy_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "user_type",
            "phone",
            "academy_id",
        ]

    def validate(self, attrs):
        # Only allow academy_admin to register coaches, players, and parents
        user_type = attrs.get("user_type")
        allowed_types = ["coach", "player", "parent"]

        if user_type not in allowed_types:
            raise serializers.ValidationError(
                {
                    "user_type": f"Academy admins can only register users of types: {', '.join(allowed_types)}"
                }
            )

        return attrs

    def create(self, validated_data):
        academy_id = validated_data.pop("academy_id")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create profile with academy association
        self.create_user_profile(user, academy_id)

        return user

    def create_user_profile(self, user, academy_id):
        """Create user profile based on user type with academy association"""
        from apps.academies.models import Academy

        try:
            academy = Academy.objects.get(id=academy_id)
        except Academy.DoesNotExist:
            raise serializers.ValidationError({"academy_id": "Academy not found"})

        profile_classes = {
            "coach": CoachProfile,
            "player": PlayerProfile,
            "parent": ParentProfile,
        }

        profile_class = profile_classes.get(user.user_type)
        if profile_class:
            profile_class.objects.create(user=user, academy=academy)


class AcademyUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for academy admins to update user information.

    Allows updating basic user information but prevents changing the user_type.
    Used by academy admins to manage users in their academy.

    Fields:
    - first_name: User's first name
    - last_name: User's last name
    - email: User's email address
    - phone: Contact phone number
    - is_active: Whether the user account is active
    """

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "is_active"]

    def validate(self, attrs):
        # Ensure user type is not changed
        if "user_type" in attrs:
            raise serializers.ValidationError(
                {"user_type": "User type cannot be changed after creation"}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing a user's password.

    Requires the old password for verification and a new password that meets
    complexity requirements. Validates that new password and confirmation match.

    Fields:
    - old_password: Current password for verification
    - new_password: New password meeting complexity requirements
    - new_password_confirm: Confirmation of new password
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("New password fields didn't match.")
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """
    Dynamic serializer for user profiles.

    Adapts to the specific profile type (coach, player, parent, etc.) and
    includes user information and calculated age.

    The model is set dynamically based on the instance type.

    Fields:
    - user: Basic user information (read-only)
    - age: Calculated from date_of_birth if available
    - All other fields from the specific profile model
    """

    user = BaseUserSerializer(read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = None  # Will be set dynamically
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.Meta.model = type(self.instance)
        # For Swagger schema generation, provide a default model if none is set
        if self.Meta.model is None:
            from apps.core.models import UserProfile

            self.Meta.model = UserProfile

    def get_age(self, obj):
        if obj.date_of_birth:
            from apps.core.utils import calculate_age

            return calculate_age(obj.date_of_birth)
        return None
