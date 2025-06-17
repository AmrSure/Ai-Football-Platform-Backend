from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.academies.urls')),
    path('api/v1/', include('apps.players.urls')),
    path('api/v1/', include('apps.matches.urls')),
    path('api/v1/', include('apps.bookings.urls')),
    path('api/v1/', include('apps.analytics.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    
    # Internationalization
    path('i18n/', include('django.conf.urls.i18n')),
]

# Add i18n patterns for admin
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    prefix_default_language=False,
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin
admin.site.site_header = "Smart Sports Management System"
admin.site.site_title = "Sports Management Admin"
admin.site.index_title = "Welcome to Sports Management System"