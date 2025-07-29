"""Serializers for the players app."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.academies.models import CoachProfile, ParentProfile, PlayerProfile
from apps.core.serializers import BaseModelSerializer

from .models import Team

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users nested within profile creation."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=False)

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
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "user_type": {"required": True},
        }

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password_confirm and password != password_confirm:
            raise serializers.ValidationError("Password fields didn't match.")

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PlayerProfileSerializer(BaseModelSerializer):
    """Serializer for PlayerProfile model with nested user creation."""

    user = UserCreateSerializer(required=False)
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    academy_name = serializers.CharField(source="academy.name", read_only=True)
    parents = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ParentProfile.objects.all(),
        required=False,
        help_text="List of parent profile IDs to associate with this player",
    )
    parents_details = serializers.SerializerMethodField()

    class Meta:
        model = PlayerProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "academy",
            "academy_name",
            "jersey_number",
            "position",
            "date_of_birth",
            "height",
            "weight",
            "dominant_foot",
            "bio",
            "parents",
            "parents_details",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_parents_details(self, obj):
        """Get parent information for the player."""
        return [
            {
                "id": parent.id,
                "user": {
                    "id": parent.user.id,
                    "email": parent.user.email,
                    "first_name": parent.user.first_name,
                    "last_name": parent.user.last_name,
                    "full_name": parent.user.get_full_name(),
                },
                "relationship": parent.relationship,
            }
            for parent in obj.parents.filter(is_active=True)
        ]

    def validate_parents(self, value):
        """Validate that all provided parents belong to the same academy as the player's academy."""
        if value:
            # Get the player's academy from the context or instance
            player_academy = None
            if self.instance:
                player_academy = self.instance.academy
            elif "academy" in self.initial_data:
                from apps.academies.models import Academy

                try:
                    player_academy = Academy.objects.get(
                        id=self.initial_data["academy"]
                    )
                except Academy.DoesNotExist:
                    pass

            # Validate all parents belong to the same academy through their children
            if player_academy:
                for parent in value:
                    # Check if parent has any children in the same academy
                    children_in_academy = parent.children.filter(
                        academy=player_academy, is_active=True
                    )
                    if not children_in_academy.exists():
                        raise serializers.ValidationError(
                            f"Parent {parent.user.get_full_name()} does not have any children in the academy {player_academy.name}"
                        )

        return value

    def validate(self, attrs):
        # If user data is provided, ensure user_type is 'player'
        user_data = attrs.get("user")
        if user_data:
            user_data["user_type"] = "player"

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop("user", None)
        parents = validated_data.pop("parents", [])

        if user_data:
            # Create user with nested data
            user_serializer = UserCreateSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            validated_data["user"] = user

            # Check if profile already exists (due to signals)
            try:
                # Try to get existing profile created by signal
                existing_profile = PlayerProfile.objects.get(user=user)
                # Update existing profile with our data
                for key, value in validated_data.items():
                    if key != "user":  # Don't overwrite user
                        setattr(existing_profile, key, value)
                existing_profile.save()

                # Set parents relationships
                if parents:
                    existing_profile.parents.set(parents)

                return existing_profile
            except PlayerProfile.DoesNotExist:
                # Profile doesn't exist, create new one
                pass

        instance = super().create(validated_data)

        # Set parents relationships
        if parents:
            instance.parents.set(parents)

        return instance

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        parents = validated_data.pop("parents", None)

        if user_data:
            # Update user data if provided
            user_serializer = UserCreateSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance = super().update(instance, validated_data)

        # Update parents relationships if provided
        if parents is not None:
            instance.parents.set(parents)

        return instance


class CoachProfileSerializer(BaseModelSerializer):
    """Serializer for CoachProfile model with nested user creation."""

    user = UserCreateSerializer(required=False)
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    academy_name = serializers.CharField(source="academy.name", read_only=True)

    class Meta:
        model = CoachProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "academy",
            "academy_name",
            "specialization",
            "experience_years",
            "certification",
            "bio",
            "date_of_birth",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        # If user data is provided, ensure user_type is 'coach'
        user_data = attrs.get("user")
        if user_data:
            user_data["user_type"] = "coach"

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop("user", None)

        if user_data:
            # Create user with nested data
            user_serializer = UserCreateSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            validated_data["user"] = user

            # Check if profile already exists (due to signals)
            try:
                # Try to get existing profile created by signal
                existing_profile = CoachProfile.objects.get(user=user)
                # Update existing profile with our data
                for key, value in validated_data.items():
                    if key != "user":  # Don't overwrite user
                        setattr(existing_profile, key, value)
                existing_profile.save()
                return existing_profile
            except CoachProfile.DoesNotExist:
                # Profile doesn't exist, create new one
                pass

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        if user_data:
            # Update user data if provided
            user_serializer = UserCreateSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        return super().update(instance, validated_data)


class ParentProfileSerializer(BaseModelSerializer):
    """Serializer for ParentProfile model with nested user creation."""

    user = UserCreateSerializer(required=False)
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    children_count = serializers.SerializerMethodField()
    children = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PlayerProfile.objects.all(),
        required=False,
        help_text="List of player profile IDs to associate as children",
    )
    children_details = serializers.SerializerMethodField()

    class Meta:
        model = ParentProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "relationship",
            "bio",
            "date_of_birth",
            "children",
            "children_details",
            "children_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_children_count(self, obj):
        """Get count of children associated with this parent."""
        return obj.children.filter(is_active=True).count()

    def get_children_details(self, obj):
        """Get detailed information about children."""
        return [
            {
                "id": child.id,
                "user": {
                    "id": child.user.id,
                    "email": child.user.email,
                    "first_name": child.user.first_name,
                    "last_name": child.user.last_name,
                    "full_name": child.user.get_full_name(),
                },
                "academy": child.academy.name if child.academy else None,
                "jersey_number": child.jersey_number,
                "position": child.position,
                "is_active": child.is_active,
            }
            for child in obj.children.filter(is_active=True)
        ]

    def validate_children(self, value):
        """Validate that all provided children belong to the same academy as the parent's academy."""
        if value:
            # Get the parent's academy from the context or instance
            parent_academy = None
            if self.instance:
                # For updates, check if parent has an academy through children
                existing_children = self.instance.children.filter(
                    academy__isnull=False
                ).first()
                if existing_children:
                    parent_academy = existing_children.academy

            # Validate all children belong to the same academy
            academy_set = set(child.academy for child in value if child.academy)
            if len(academy_set) > 1:
                raise serializers.ValidationError(
                    "All children must belong to the same academy."
                )

            # If parent has an academy context, ensure children match
            if parent_academy and academy_set and parent_academy not in academy_set:
                raise serializers.ValidationError(
                    f"Children must belong to the same academy as the parent: {parent_academy.name}"
                )

        return value

    def validate(self, attrs):
        # If user data is provided, ensure user_type is 'parent'
        user_data = attrs.get("user")
        if user_data:
            user_data["user_type"] = "parent"

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop("user", None)
        children = validated_data.pop("children", [])

        if user_data:
            # Create user with nested data
            user_serializer = UserCreateSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()
            validated_data["user"] = user

            # Check if profile already exists (due to signals)
            try:
                # Try to get existing profile created by signal
                existing_profile = ParentProfile.objects.get(user=user)
                # Update existing profile with our data
                for key, value in validated_data.items():
                    if key != "user":  # Don't overwrite user
                        setattr(existing_profile, key, value)
                existing_profile.save()

                # Set children relationships
                if children:
                    existing_profile.children.set(children)

                return existing_profile
            except ParentProfile.DoesNotExist:
                # Profile doesn't exist, create new one
                pass

        instance = super().create(validated_data)

        # Set children relationships
        if children:
            instance.children.set(children)

        return instance

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        children = validated_data.pop("children", None)

        if user_data:
            # Update user data if provided
            user_serializer = UserCreateSerializer(
                instance.user, data=user_data, partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        instance = super().update(instance, validated_data)

        # Update children relationships if provided
        if children is not None:
            instance.children.set(children)

        return instance


class TeamSerializer(BaseModelSerializer):
    """Serializer for Team model."""

    academy_name = serializers.CharField(source="academy.name", read_only=True)
    coach_name = serializers.CharField(
        source="coach.user.get_full_name", read_only=True
    )
    players_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "academy",
            "academy_name",
            "coach",
            "coach_name",
            "age_group",
            "formation",
            "players_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_players_count(self, obj):
        """Get count of active players in this team."""
        return obj.players.filter(is_active=True).count()


class TeamDetailSerializer(TeamSerializer):
    """Detailed serializer for Team model with nested players."""

    players = PlayerProfileSerializer(many=True, read_only=True)

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields + ["players"]
