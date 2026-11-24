from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Core public landing
    path('', include('core.urls')),

    # Authentication
    path('', include('accounts.urls')),

    # Student portal
    path('', include('students.urls')),
    path('', include('academics.urls')),
    path('', include('companies.urls')),
    path('', include('discipline.urls')),

    # Administrator Portal
    path('admin-dashboard/', include('accounts.admin_urls', namespace='admin_dashboard')),

    # Django built-in admin
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
