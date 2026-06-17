from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("<slug:slug>/", views.EventFormView.as_view(), name="event-form"),
]
