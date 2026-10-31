from django.contrib import admin
from .models import Atividade, Evento, InscricaoAtividade, InscricaoEvento, Sala


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'bloco', 'capacidade']
    search_fields = ['nome', 'bloco']
    list_filter = ['bloco']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'organizador', 'data_inicio', 'data_fim', 'inscricoes_abertas']
    list_filter = ['inscricoes_abertas', 'data_inicio']
    search_fields = ['nome', 'descricao', 'organizador__username']
    readonly_fields = ['organizador']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.organizador = request.user
        super().save_model(request, obj, form, change)


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'evento', 'tipo', 'sala', 'inicio', 'fim', 'vagas_restantes']
    list_filter = ['evento', 'tipo', 'sala']
    search_fields = ['titulo', 'responsavel', 'evento__nome']


@admin.register(InscricaoEvento)
class InscricaoEventoAdmin(admin.ModelAdmin):
    list_display = ['evento', 'participante', 'data']
    list_filter = ['evento']
    search_fields = ['evento__nome', 'participante__username']
    readonly_fields = ['evento', 'participante', 'data']

    def has_add_permission(self, request):
        return False


@admin.register(InscricaoAtividade)
class InscricaoAtividadeAdmin(admin.ModelAdmin):
    list_display = ['atividade', 'inscricao_evento', 'data']
    list_filter = ['atividade__evento', 'atividade']
    search_fields = ['atividade__titulo', 'inscricao_evento__participante__username']
    readonly_fields = ['atividade', 'inscricao_evento', 'data']

    def has_add_permission(self, request):
        return False


admin.site.site_header = 'Eventos do campus — Administração'
admin.site.site_title = 'Eventos IFPB'
admin.site.index_title = 'Salas e programação'
