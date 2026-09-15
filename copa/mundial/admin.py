from django.contrib import admin


from .models import Arbitro, Estadio, Grupo, Partida, Selecao, Tecnico
admin.site.register(Estadio)
class SelecaoInline(admin.TabularInline):
    model = Selecao
    extra = 0
    fields = ("nome", "sigla")


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ("letra", "total_de_selecoes")
    inlines = [SelecaoInline]

    @admin.display(description="Seleções")
    def total_de_selecoes(self, obj):
        return obj.selecoes.count()
class PessoaAdmin(admin.ModelAdmin):
    list_display = ("nome", "pais")
    search_fields = ("nome", "pais")
    list_filter = ("pais",)
admin.site.register(Tecnico, PessoaAdmin)
admin.site.register(Arbitro, PessoaAdmin)
@admin.register(Selecao)
class SelecaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "grupo")
    list_filter = ("grupo",)
    search_fields = ("nome", "sigla")
    ordering = ("nome",)
@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ("mandante", "visitante", "resultado", "fase", "encerrada")
    list_filter = ("fase", "grupo", "encerrada")
    date_hierarchy = "data_hora"
    list_editable = ("encerrada",)

    @admin.display(description="Placar")
    def resultado(self, obj):
        return obj.placar()

    fieldsets = (
        ("Confronto", {
            "fields": ("fase", "grupo", "mandante", "visitante"),
        }),
        ("Local e data", {
            "fields": ("estadio", "data_hora", "arbitros"),
        }),
        ("Resultado", {
            "fields": ("encerrada", "gols_mandante", "gols_visitante"),
        }),
        ("Controle", {
            "fields": ("registrada_em", "atualizada_em"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("registrada_em", "atualizada_em")

admin.site.site_header = "Copa do Mundo — Administração"
admin.site.site_title = "Copa do Mundo"
admin.site.index_title = "Registro de jogos"
