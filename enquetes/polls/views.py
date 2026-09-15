from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_criar(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    corpo = json.loads(request.body)
    nova = {
        "id": len(PERGUNTAS) + 1,
        "texto": corpo["texto"],
        "votos": 0,
    }
    PERGUNTAS.append(nova)

    return JsonResponse({"resultado": nova}, status=201)



def api_lista(request):
    return JsonResponse(PERGUNTAS, safe=False)

def api_detalhe(request, pergunta_id):
    pergunta = buscar_pergunta(pergunta_id)

    if pergunta is None:
        return JsonResponse(
            {"erro": "Pergunta não encontrada"},
            status=404,
        )

    return JsonResponse({"resultado": pergunta})

def api_info(request):
    return JsonResponse({
        "aplicacao": "Enquetes IFPB",
        "versao": "1.0",
        "total_perguntas": len(PERGUNTAS),
    })


PERGUNTAS = [
    {"id": 1, "texto": "Qual sua linguagem de programação favorita?", "votos": 0},
    {"id": 2, "texto": "Qual framework web você prefere?", "votos": 0},
    {"id": 3, "texto": "Você prefere FBV ou CBV?", "votos": 0},
]

def buscar_pergunta(pergunta_id):
    for pergunta in PERGUNTAS:
        if pergunta["id"] == pergunta_id:
            return pergunta
    return None


def index(request):
    link = reverse("polls:detalhe",args=[1])
    html = f'<h1>Enquetes</h1><a href="{link}">Ver enquete 1</a>'
    return HttpResponse(html)

def detalhe(request, pergunta_id):
    return HttpResponse(f"Você está vendo a pergunta {pergunta_id}")

class VotarView(View):

    def get(self, request, pergunta_id):
        return HttpResponse(f"Formulário de votação da enquete {pergunta_id}")

    def post(self, request, pergunta_id):
        return HttpResponse(f"Voto registrado na enquete {pergunta_id}")

def relatorio(request):
    linhas = [f'{p["id"]}: {p["texto"]}' for p in PERGUNTAS]
    conteudo = "\n".join(linhas)
    return HttpResponse(conteudo, content_type="text/plain; charset=utf-8")
