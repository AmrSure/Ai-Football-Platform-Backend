from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "academies"

# Router for academy management
router = DefaultRouter()
router.register(r"academy", views.AcademyViewSet, basename="academy")
router.register(r"academy-admins", views.AcademyAdminProfileViewSet)
router.register(r"external-clients", views.ExternalClientProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
