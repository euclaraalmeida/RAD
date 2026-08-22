from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    path("", views.index, name = "index"),
    path("<int:pergunta_id>/",views.detalhe, name= "detalhe"),
    path("<int:pergunta_id>/votar/", views.VotarView.as_view(), name="votar"),
    path("relatorio/", views.relatorio, name="relatorio"),
    path("api/info/", views.api_info, name="api_info"),
    path("api/perguntas/", views.api_lista, name="api_lista"),
    path("api/perguntas/<int:pergunta_id>/", views.api_detalhe, name="api_detalhe"),
    path("api/perguntas/criar/", views.api_criar, name="api_criar"),



]
