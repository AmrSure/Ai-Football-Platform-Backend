from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "notifications"

# Router for notifications
router = DefaultRouter()
router.register(r"notifications", views.NotificationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
