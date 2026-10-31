"""Regras das inscrições, verificadas na transação que grava os dados."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Atividade, Evento, InscricaoAtividade, InscricaoEvento


@transaction.atomic
def inscrever_evento(participante, evento_id):
    evento = get_object_or_404(Evento, pk=evento_id)
    if InscricaoEvento.objects.filter(evento=evento, participante=participante).exists():
        raise ValidationError('Você já está inscrito neste evento.')
    inscricao = InscricaoEvento(evento=evento, participante=participante)
    inscricao.full_clean()
    inscricao.save()
    return inscricao


@transaction.atomic
def inscrever_atividade(participante, atividade_id):
    atividade = get_object_or_404(Atividade.objects.select_related('evento', 'sala'), pk=atividade_id)
    inscricao_evento = InscricaoEvento.objects.filter(evento=atividade.evento, participante=participante).first()
    if not inscricao_evento:
        raise ValidationError('Inscreva-se primeiro no evento desta atividade.')
    if InscricaoAtividade.objects.filter(inscricao_evento=inscricao_evento, atividade=atividade).exists():
        raise ValidationError('Você já está inscrito nesta atividade.')
    inscricao = InscricaoAtividade(inscricao_evento=inscricao_evento, atividade=atividade)
    inscricao.full_clean()
    inscricao.save()
    return inscricao


@transaction.atomic
def cancelar_evento(participante, inscricao_id):
    inscricao = get_object_or_404(InscricaoEvento, pk=inscricao_id, participante=participante)
    evento_id = inscricao.evento_id
    inscricao.delete()
    return evento_id


@transaction.atomic
def cancelar_atividade(participante, inscricao_id):
    inscricao = get_object_or_404(InscricaoAtividade, pk=inscricao_id, inscricao_evento__participante=participante)
    evento_id = inscricao.atividade.evento_id
    inscricao.delete()
    return evento_id
