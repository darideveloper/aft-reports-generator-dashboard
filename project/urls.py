from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import include, path

from rest_framework import routers

from survey import views as survey_views


# Setup drf router
router = routers.DefaultRouter()
router.register(
    r'companies',
    survey_views.CompanyViewSet,
    basename='companies'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Redirects
    path(
        '',
        RedirectView.as_view(url='/admin/'),
        name='home-redirect-admin'
    ),
    path(
        'accounts/login/',
        RedirectView.as_view(url='/admin/'),
        name='login-redirect-admin'
    ),
    
    # API URLs
    path('api/', include(router.urls)),
]
