from django.urls import path

from . import views

app_name = "mundial"

urlpatterns = [
    path("grupos/<str:letra>/", views.api_grupo, name="api_grupo"),
]

