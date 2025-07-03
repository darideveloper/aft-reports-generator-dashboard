from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import include, path


from rest_framework import routers


# Setup drf router
router = routers.DefaultRouter()

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
