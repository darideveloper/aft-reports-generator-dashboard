from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers

from survey import views as survey_views


# Setup drf router
router = routers.DefaultRouter()
router.register(r"companies", survey_views.CompanyViewSet, basename="companies")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirects
    path("", RedirectView.as_view(url="/admin/"), name="home-redirect-admin"),
    path(
        "accounts/login/",
        RedirectView.as_view(url="/admin/"),
        name="login-redirect-admin",
    ),
    # API URLs
    path("api/", include(router.urls)),
    path(
        "api/invitation/",
        survey_views.InvitationCodeView.as_view(),
        name="invitation-code",
    ),
]

if not settings.STORAGE_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
