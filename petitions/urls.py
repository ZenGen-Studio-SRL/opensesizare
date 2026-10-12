from django.urls import path

from . import views

app_name = "petitions"

urlpatterns = [
    path("", views.municipality_list, name="index"),
    path("p/<slug:slug>/", views.submit, name="submit"),
    path("status/<str:code>/", views.status, name="status"),
]
