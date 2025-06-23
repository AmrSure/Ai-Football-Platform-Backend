from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "players"

# Router for player management
router = DefaultRouter()
router.register(r"players", views.PlayerProfileViewSet)
router.register(r"coaches", views.CoachProfileViewSet)
router.register(r"parents", views.ParentProfileViewSet)
router.register(r"teams", views.TeamViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
