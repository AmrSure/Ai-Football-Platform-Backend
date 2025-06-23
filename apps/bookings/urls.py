from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "bookings"

# Router for booking management
router = DefaultRouter()
router.register(r"fields", views.FieldViewSet)
router.register(r"bookings", views.FieldBookingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
