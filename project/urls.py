from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers

from survey import views as survey_views


# Setup drf router
router = routers.DefaultRouter()
router.register(r"surveys", survey_views.SurveyDetailView, basename="surveys")

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
    
    # No crud endpoints
    path(
        "api/invitation-code/",
        survey_views.InvitationCodeView.as_view(),
        name="invitation-code",
    ),
    path(
        "report/<int:survey_id>/<int:participant_id>/",
        survey_views.ReportView.as_view(),
        name="report",
    ),
]

if not settings.STORAGE_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
