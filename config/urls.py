from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

# Base URL's
# ------------------------------------------------------------------------------
urlpatterns = [
    path("", include("apps.common.urls")),
    path("", include("apps.learning.urls")),
    path("", include("apps.access.urls")),
    path("", include("apps.cms.urls")),
    path("", include("apps.web_portal.urls")),
    path("", include("apps.service_idp.urls")),
    path("", include("apps.my_learnings.urls")),
    path("", include("apps.purchase.urls")),
    path("", include("apps.jobs.urls")),
    path("", include("apps.forums.urls")),
    path("", include("apps.hackathons.urls")),
    path("", include("apps.blogs.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

# Static & Media Files
# ------------------------------------------------------------------------------
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()
