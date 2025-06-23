"""Serializers for the analytics app."""

from rest_framework import serializers


class AcademyOverviewSerializer(serializers.Serializer):
    """Serializer for academy overview statistics."""

    academy_id = serializers.IntegerField()
    academy_name = serializers.CharField()
    total_players = serializers.IntegerField()
    total_coaches = serializers.IntegerField()
    total_teams = serializers.IntegerField()
    total_matches = serializers.IntegerField()
    total_fields = serializers.IntegerField()
    active_bookings = serializers.IntegerField()


class PlayerPerformanceStatsSerializer(serializers.Serializer):
    """Serializer for player performance statistics."""

    total_players = serializers.IntegerField()
    average_age = serializers.FloatField()
    position_distribution = serializers.DictField()
    top_performers = serializers.ListField()


class TeamPerformanceStatsSerializer(serializers.Serializer):
    """Serializer for team performance statistics."""

    total_teams = serializers.IntegerField()
    average_team_size = serializers.FloatField()
    category_distribution = serializers.DictField()
    top_teams = serializers.ListField()


class FieldUtilizationStatsSerializer(serializers.Serializer):
    """Serializer for field utilization statistics."""

    total_fields = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    utilization_rate = serializers.FloatField()
    most_popular_fields = serializers.ListField()
    booking_trends = serializers.DictField()
