from django.urls import path
from . import views

app_name = 'programacao'
urlpatterns = [
    path('', views.lista, name='lista'),
    path('eventos/novo/', views.NovoEvento.as_view(), name='novo_evento'),
    path('eventos/<int:pk>/', views.detalhe, name='detalhe'),
    path('eventos/<int:pk>/editar/', views.EditarEvento.as_view(), name='editar_evento'),
    path('eventos/<int:pk>/excluir/', views.ExcluirEvento.as_view(), name='excluir_evento'),
    path('eventos/<int:pk>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    path('eventos/<int:pk>/painel/', views.Painel.as_view(), name='painel'),
    path('eventos/<int:evento_id>/atividades/nova/', views.NovaAtividade.as_view(), name='nova_atividade'),
    path('eventos/<int:evento_id>/atividades/<int:pk>/editar/', views.EditarAtividade.as_view(), name='editar_atividade'),
    path('eventos/<int:evento_id>/atividades/<int:pk>/excluir/', views.ExcluirAtividade.as_view(), name='excluir_atividade'),
    path('atividades/<int:pk>/inscrever/', views.inscrever_atividade, name='inscrever_atividade'),
    path('inscricoes/eventos/<int:pk>/cancelar/', views.cancelar_evento, name='cancelar_evento'),
    path('inscricoes/atividades/<int:pk>/cancelar/', views.cancelar_atividade, name='cancelar_atividade'),
    path('minha-agenda/', views.agenda, name='agenda'),
    path('meus-eventos/', views.meus_eventos, name='meus_eventos'),
]
