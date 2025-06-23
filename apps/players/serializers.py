"""Serializers for the players app."""

from rest_framework import serializers

from apps.academies.models import CoachProfile, ParentProfile, PlayerProfile
from apps.core.serializers import BaseModelSerializer

from .models import Team


class PlayerProfileSerializer(BaseModelSerializer):
    """Serializer for PlayerProfile model."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    academy_name = serializers.CharField(source="academy.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = PlayerProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "academy",
            "academy_name",
            "team",
            "team_name",
            "jersey_number",
            "position",
            "date_of_birth",
            "height",
            "weight",
            "dominant_foot",
            "bio",
            "emergency_contact_name",
            "emergency_contact_phone",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CoachProfileSerializer(BaseModelSerializer):
    """Serializer for CoachProfile model."""

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
            "certifications",
            "bio",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ParentProfileSerializer(BaseModelSerializer):
    """Serializer for ParentProfile model."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    academy_name = serializers.CharField(source="academy.name", read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = ParentProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "academy",
            "academy_name",
            "relationship",
            "children_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_children_count(self, obj):
        """Get count of children associated with this parent."""
        return obj.children.filter(is_active=True).count()


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
