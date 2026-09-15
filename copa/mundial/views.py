
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Grupo


def api_grupo(request, letra):
    grupo = get_object_or_404(Grupo, letra=letra.upper())

    selecoes = [
        {"nome": s.nome, "sigla": s.sigla}
        for s in grupo.selecoes.all()
    ]

    partidas = [
        {
            "confronto": str(p),
            "fase": p.get_fase_display(),
            "placar": p.placar(),
        }
        for p in grupo.partidas.all()
    ]

    return JsonResponse({
        "grupo": grupo.letra,
        "selecoes": selecoes,
        "partidas": partidas,
    })

