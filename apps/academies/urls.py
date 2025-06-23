from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "academies"

# Router for academy management
router = DefaultRouter()
router.register(r"academies", views.AcademyViewSet)
router.register(r"academy-admins", views.AcademyAdminProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
