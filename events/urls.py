from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("<slug:slug>/access/", views.EventAccessView.as_view(), name="event-access"),
    path("<slug:slug>/ics/", views.EventCalendarIcsView.as_view(), name="event-ics"),
    path("<slug:slug>/", views.EventFormView.as_view(), name="event-form"),
]
