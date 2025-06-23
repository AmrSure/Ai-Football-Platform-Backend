from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "matches"

# Router for match management
router = DefaultRouter()
router.register(r"matches", views.MatchViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
