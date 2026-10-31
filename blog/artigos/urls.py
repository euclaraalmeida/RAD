from django.urls import path
from . import views

app_name = 'artigos'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('categoria/<slug:slug>/', views.por_categoria, name='por_categoria'),
    path('busca/', views.busca, name='busca'),
    path('novo/', views.novo, name='novo'),
    path('meus-posts/', views.meus_posts, name='meus_posts'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('post/<slug:slug>/', views.detalhe, name='detalhe'),
    path('post/<slug:slug>/editar/', views.EditarPost.as_view(), name='editar'),
    path('post/<slug:slug>/excluir/', views.excluir, name='excluir'),
]
