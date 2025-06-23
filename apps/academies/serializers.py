from rest_framework import serializers

from apps.core.serializers import BaseUserSerializer

from .models import (
    Academy,
    AcademyAdminProfile,
    CoachProfile,
    ExternalClientProfile,
    ParentProfile,
    PlayerProfile,
)


class CoachProfileNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for coach profiles within academy details.
    """

    user = BaseUserSerializer(read_only=True)

    class Meta:
        model = CoachProfile
        fields = [
            "id",
            "user",
            "specialization",
            "experience_years",
            "certification",
            "bio",
            "date_of_birth",
            "is_active",
            "created_at",
        ]


class PlayerProfileNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for player profiles within academy details.
    """

    user = BaseUserSerializer(read_only=True)
    parents = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()

    class Meta:
        model = PlayerProfile
        fields = [
            "id",
            "user",
            "jersey_number",
            "position",
            "height",
            "weight",
            "dominant_foot",
            "bio",
            "date_of_birth",
            "parents",
            "teams",
            "is_active",
            "created_at",
        ]

    def get_parents(self, obj):
        """Get parent information for the player."""
        return [
            {
                "id": parent.id,
                "user": {
                    "id": parent.user.id,
                    "email": parent.user.email,
                    "first_name": parent.user.first_name,
                    "last_name": parent.user.last_name,
                },
                "relationship": parent.relationship,
            }
            for parent in obj.parents.filter(is_active=True)
        ]

    def get_teams(self, obj):
        """Get team information for the player."""
        return [
            {
                "id": team.id,
                "name": team.name,
                "age_group": team.age_group,
                "formation": team.formation,
            }
            for team in obj.teams.filter(is_active=True)
        ]


class ParentProfileNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for parent profiles within academy details.
    """

    user = BaseUserSerializer(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = ParentProfile
        fields = [
            "id",
            "user",
            "relationship",
            "bio",
            "date_of_birth",
            "children",
            "is_active",
            "created_at",
        ]

    def get_children(self, obj):
        """Get children information for the parent."""
        return [
            {
                "id": child.id,
                "user": {
                    "id": child.user.id,
                    "email": child.user.email,
                    "first_name": child.user.first_name,
                    "last_name": child.user.last_name,
                },
                "jersey_number": child.jersey_number,
                "position": child.position,
            }
            for child in obj.children.filter(is_active=True)
        ]


class AcademyAdminProfileNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for academy admin profiles within academy details.
    """

    user = BaseUserSerializer(read_only=True)

    class Meta:
        model = AcademyAdminProfile
        fields = [
            "id",
            "user",
            "position",
            "bio",
            "date_of_birth",
            "is_active",
            "created_at",
        ]


class AcademyDetailSerializer(serializers.ModelSerializer):
    """
    Detailed academy serializer with all nested objects.
    Used for retrieve operations to provide comprehensive academy information.
    """

    admins = AcademyAdminProfileNestedSerializer(many=True, read_only=True)
    coaches = CoachProfileNestedSerializer(many=True, read_only=True)
    players = PlayerProfileNestedSerializer(many=True, read_only=True)
    teams = serializers.SerializerMethodField()
    fields = serializers.SerializerMethodField()

    # Statistics
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Academy
        fields = [
            "id",
            "name",
            "name_ar",
            "description",
            "logo",
            "address",
            "phone",
            "email",
            "website",
            "established_date",
            "is_active",
            "created_at",
            "updated_at",
            "admins",
            "coaches",
            "players",
            "teams",
            "fields",
            "statistics",
        ]

    def get_teams(self, obj):
        """Get teams information for the academy."""
        try:
            # Try to get teams from the related manager
            teams_queryset = getattr(obj, "teams", obj.team_set).filter(is_active=True)

            teams_data = []
            for team in teams_queryset:
                team_data = {
                    "id": team.id,
                    "name": team.name,
                    "age_group": team.age_group,
                    "formation": getattr(team, "formation", ""),
                    "is_active": team.is_active,
                    "created_at": team.created_at,
                    "total_players": team.players.filter(is_active=True).count(),
                }

                # Add coach information if available
                if hasattr(team, "coach") and team.coach and team.coach.is_active:
                    team_data["coach"] = {
                        "id": team.coach.id,
                        "user": {
                            "id": team.coach.user.id,
                            "email": team.coach.user.email,
                            "first_name": team.coach.user.first_name,
                            "last_name": team.coach.user.last_name,
                        },
                        "specialization": team.coach.specialization,
                        "experience_years": team.coach.experience_years,
                    }
                else:
                    team_data["coach"] = None

                # Add players information
                team_data["players"] = [
                    {
                        "id": player.id,
                        "user": {
                            "id": player.user.id,
                            "email": player.user.email,
                            "first_name": player.user.first_name,
                            "last_name": player.user.last_name,
                        },
                        "jersey_number": player.jersey_number,
                        "position": player.position,
                    }
                    for player in team.players.filter(is_active=True)
                ]

                teams_data.append(team_data)

            return teams_data
        except Exception:
            return []

    def get_fields(self, obj):
        """Get fields information for the academy."""
        try:
            fields_data = []
            for field in obj.fields.filter(is_active=True):
                field_data = {
                    "id": field.id,
                    "name": field.name,
                    "field_type": field.field_type,
                    "capacity": field.capacity,
                    "hourly_rate": str(field.hourly_rate),
                    "facilities": field.facilities,
                    "is_available": field.is_available,
                    "is_active": field.is_active,
                    "created_at": field.created_at,
                }

                # Add upcoming bookings
                try:
                    from datetime import timedelta

                    from django.utils import timezone

                    # Get bookings for the next 7 days
                    end_date = timezone.now() + timedelta(days=7)
                    upcoming = field.bookings.filter(
                        start_time__gte=timezone.now(),
                        start_time__lte=end_date,
                        status__in=["confirmed", "pending"],
                    ).order_by("start_time")[
                        :5
                    ]  # Limit to 5 upcoming bookings

                    field_data["upcoming_bookings"] = [
                        {
                            "id": booking.id,
                            "start_time": booking.start_time,
                            "end_time": booking.end_time,
                            "status": booking.status,
                            "booked_by": {
                                "id": booking.booked_by.id,
                                "email": booking.booked_by.email,
                                "first_name": booking.booked_by.first_name,
                                "last_name": booking.booked_by.last_name,
                            },
                        }
                        for booking in upcoming
                    ]
                except Exception:
                    field_data["upcoming_bookings"] = []

                fields_data.append(field_data)

            return fields_data
        except Exception:
            return []

    def get_statistics(self, obj):
        """Get comprehensive statistics for the academy."""
        # Get active counts
        active_coaches = obj.coaches.filter(is_active=True)
        active_players = obj.players.filter(is_active=True)
        try:
            active_teams = getattr(obj, "teams", obj.team_set).filter(is_active=True)
        except Exception:
            active_teams = []
        active_fields = obj.fields.filter(is_active=True)

        # Get parents count (related through players)
        parent_ids = set()
        for player in active_players:
            for parent in player.parents.filter(is_active=True):
                parent_ids.add(parent.id)

        return {
            "total_admins": obj.admins.filter(is_active=True).count(),
            "total_coaches": active_coaches.count(),
            "total_players": active_players.count(),
            "total_parents": len(parent_ids),
            "total_teams": len(active_teams)
            if hasattr(active_teams, "__len__")
            else active_teams.count(),
            "total_fields": active_fields.count(),
            "coaches_by_specialization": self._get_coaches_by_specialization(
                active_coaches
            ),
            "players_by_position": self._get_players_by_position(active_players),
            "teams_by_age_group": self._get_teams_by_age_group(active_teams),
            "fields_by_type": self._get_fields_by_type(active_fields),
        }

    def _get_coaches_by_specialization(self, coaches):
        """Group coaches by specialization."""
        specializations = {}
        for coach in coaches:
            spec = coach.specialization or "Not Specified"
            specializations[spec] = specializations.get(spec, 0) + 1
        return specializations

    def _get_players_by_position(self, players):
        """Group players by position."""
        positions = {}
        for player in players:
            pos = player.position or "Not Specified"
            positions[pos] = positions.get(pos, 0) + 1
        return positions

    def _get_teams_by_age_group(self, teams):
        """Group teams by age group."""
        age_groups = {}
        try:
            for team in teams:
                age = getattr(team, "age_group", None) or "Not Specified"
                age_groups[age] = age_groups.get(age, 0) + 1
        except Exception:
            pass
        return age_groups

    def _get_fields_by_type(self, fields):
        """Group fields by type."""
        field_types = {}
        try:
            for field in fields:
                field_type = getattr(
                    field, "get_field_type_display", lambda: field.field_type
                )()
                field_types[field_type] = field_types.get(field_type, 0) + 1
        except Exception:
            pass
        return field_types


class AcademySerializer(serializers.ModelSerializer):
    """
    Basic academy serializer for list operations.
    Does not include nested objects for performance.
    """

    basic_statistics = serializers.SerializerMethodField()

    class Meta:
        model = Academy
        fields = [
            "id",
            "name",
            "name_ar",
            "description",
            "logo",
            "address",
            "phone",
            "email",
            "website",
            "established_date",
            "is_active",
            "created_at",
            "updated_at",
            "basic_statistics",
        ]

    def get_basic_statistics(self, obj):
        """Get basic count statistics for the academy."""
        return {
            "total_coaches": obj.coaches.filter(is_active=True).count(),
            "total_players": obj.players.filter(is_active=True).count(),
            "total_teams": getattr(obj, "teams", obj.team_set)
            .filter(is_active=True)
            .count(),
            "total_fields": obj.fields.filter(is_active=True).count(),
        }


class AcademyAdminProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for academy admin profiles.
    """

    user = BaseUserSerializer(read_only=True)
    academy_name = serializers.CharField(source="academy.name", read_only=True)

    class Meta:
        model = AcademyAdminProfile
        fields = [
            "id",
            "user",
            "academy",
            "academy_name",
            "position",
            "bio",
            "date_of_birth",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]
