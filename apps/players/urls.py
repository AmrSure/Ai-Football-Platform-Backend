from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "players"

# Router for player management
router = DefaultRouter()
router.register(r"playerprofile", views.PlayerProfileViewSet, basename="playerprofile")
router.register(r"coachprofile", views.CoachProfileViewSet, basename="coachprofile")
router.register(r"parentprofile", views.ParentProfileViewSet, basename="parentprofile")
router.register(r"team", views.TeamViewSet, basename="team")

urlpatterns = [
    path("players/", include(router.urls)),
]
