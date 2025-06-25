from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "bookings"

# Router for booking management
router = DefaultRouter()
router.register(r"field", views.FieldViewSet, basename="field")
router.register(r"fieldbooking", views.FieldBookingViewSet, basename="fieldbooking")

urlpatterns = [
    path("", include(router.urls)),
]
