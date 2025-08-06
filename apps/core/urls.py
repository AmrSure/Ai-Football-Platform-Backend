"""Core app URL Configuration."""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("dashboardstats/", views.DashboardStatsView.as_view(), name="dashboard-stats"),
    path("health/", views.health_check, name="health-check"),
]
