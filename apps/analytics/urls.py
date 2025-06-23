from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "analytics"

# Router for analytics
router = DefaultRouter()
router.register(r"analytics", views.AnalyticsViewSet, basename="analytics")

urlpatterns = [
    path("", include(router.urls)),
]
