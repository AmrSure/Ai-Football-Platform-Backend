from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

# Router for system admin user management
router = DefaultRouter()
router.register(r"users", views.UserViewSet)

# Router for academy admin user management
academy_router = DefaultRouter()
academy_router.register(
    r"academy-users", views.AcademyUserViewSet, basename="academy-users"
)

urlpatterns = [
    # Authentication
    path(
        "auth/login/",
        views.CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "auth/change-password/",
        views.ChangePasswordView.as_view(),
        name="change_password",
    ),
    # Academy user management
    path(
        "auth/academy/register-user/",
        views.AcademyUserRegistrationView.as_view(),
        name="academy_register_user",
    ),
    # User management
    path("", include(router.urls)),
    path("", include(academy_router.urls)),
]
