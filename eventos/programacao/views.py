from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from . import services
from .forms import AtividadeForm, EventoForm
from .models import Atividade, Evento, InscricaoAtividade, InscricaoEvento


def lista(request):
    return render(request, 'programacao/lista.html', {'eventos': Evento.objects.select_related('organizador')})


def detalhe(request, pk):
    evento = get_object_or_404(Evento.objects.select_related('organizador'), pk=pk)
    inscricao_evento = None
    agenda = []
    if request.user.is_authenticated:
        inscricao_evento = evento.inscricoes.filter(participante=request.user).first()
        agenda = list(InscricaoAtividade.objects.filter(inscricao_evento__participante=request.user).select_related('atividade'))
    programacao = []
    for atividade in evento.atividades.select_related('sala').prefetch_related('inscricoes'):
        inscricao = next((i for i in agenda if i.atividade_id == atividade.pk), None)
        conflito = any(i.atividade.inicio < atividade.fim and i.atividade.fim > atividade.inicio for i in agenda)
        vagas = atividade.vagas_restantes
        pode_inscrever = bool(inscricao_evento and not inscricao and vagas > 0 and not conflito and evento.inscricoes_abertas)
        programacao.append({'atividade': atividade, 'inscricao': inscricao, 'vagas': vagas, 'conflito': conflito, 'pode_inscrever': pode_inscrever})
    return render(request, 'programacao/detalhe.html', {'evento': evento, 'programacao': programacao, 'inscricao_evento': inscricao_evento})


@method_decorator(transaction.atomic, name='dispatch')
class NovoEvento(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    http_method_names = ['get', 'post', 'head', 'options']
    permission_required = 'programacao.add_evento'
    model = Evento
    form_class = EventoForm
    template_name = 'programacao/form.html'
    extra_context = {'titulo': 'Criar evento'}

    def form_valid(self, form):
        form.instance.organizador = self.request.user
        resposta = super().form_valid(form)
        messages.success(self.request, 'Evento criado com sucesso.')
        return resposta


class EventoProprioMixin(LoginRequiredMixin, PermissionRequiredMixin):
    http_method_names = ['get', 'post', 'head', 'options']
    model = Evento

    def get_queryset(self):
        return Evento.objects.filter(organizador=self.request.user)


@method_decorator(transaction.atomic, name='dispatch')
class EditarEvento(EventoProprioMixin, UpdateView):
    permission_required = 'programacao.change_evento'
    form_class = EventoForm
    template_name = 'programacao/form.html'
    extra_context = {'titulo': 'Editar evento'}

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, 'Evento atualizado com sucesso.')
        return resposta


@method_decorator(transaction.atomic, name='dispatch')
class ExcluirEvento(EventoProprioMixin, DeleteView):
    permission_required = 'programacao.delete_evento'
    template_name = 'programacao/confirmar_exclusao.html'
    success_url = reverse_lazy('programacao:lista')

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, 'Evento e inscrições vinculadas excluídos.')
        return resposta


class AtividadeFormMixin(LoginRequiredMixin, PermissionRequiredMixin):
    http_method_names = ['get', 'post', 'head', 'options']
    model = Atividade
    form_class = AtividadeForm
    template_name = 'programacao/form.html'

    def get_evento(self):
        return get_object_or_404(Evento, pk=self.kwargs['evento_id'], organizador=self.request.user)

    def get_queryset(self):
        return Atividade.objects.filter(evento=self.get_evento())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['evento'] = self.get_evento()
        return kwargs

    def get_success_url(self):
        return self.get_evento().get_absolute_url()

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, 'Atividade salva com sucesso.')
        return resposta


@method_decorator(transaction.atomic, name='dispatch')
class NovaAtividade(AtividadeFormMixin, CreateView):
    permission_required = 'programacao.add_atividade'
    extra_context = {'titulo': 'Criar atividade'}


@method_decorator(transaction.atomic, name='dispatch')
class EditarAtividade(AtividadeFormMixin, UpdateView):
    permission_required = 'programacao.change_atividade'
    extra_context = {'titulo': 'Editar atividade'}


@method_decorator(transaction.atomic, name='dispatch')
class ExcluirAtividade(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    http_method_names = ['get', 'post', 'head', 'options']
    permission_required = 'programacao.delete_atividade'
    model = Atividade
    template_name = 'programacao/confirmar_exclusao.html'

    def get_queryset(self):
        return Atividade.objects.filter(evento_id=self.kwargs['evento_id'], evento__organizador=self.request.user)

    def get_success_url(self):
        return self.object.evento.get_absolute_url()

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, 'Atividade excluída com sucesso.')
        return resposta


@login_required
@require_POST
def inscrever_evento(request, pk):
    try:
        services.inscrever_evento(request.user, pk)
        messages.success(request, 'Inscrição no evento realizada.')
    except ValidationError as erro:
        messages.error(request, ' '.join(erro.messages))
    return redirect('programacao:detalhe', pk=pk)


@login_required
@require_POST
def inscrever_atividade(request, pk):
    atividade = get_object_or_404(Atividade, pk=pk)
    try:
        services.inscrever_atividade(request.user, pk)
        messages.success(request, 'Inscrição na atividade realizada.')
    except ValidationError as erro:
        messages.error(request, ' '.join(erro.messages))
    return redirect(atividade.evento)


@login_required
@require_POST
def cancelar_evento(request, pk):
    evento_id = services.cancelar_evento(request.user, pk)
    messages.success(request, 'Inscrição no evento e em suas atividades cancelada.')
    return redirect('programacao:detalhe', pk=evento_id)


@login_required
@require_POST
def cancelar_atividade(request, pk):
    services.cancelar_atividade(request.user, pk)
    messages.success(request, 'Inscrição na atividade cancelada. A vaga foi liberada.')
    return redirect('programacao:agenda')


@login_required
def agenda(request):
    inscricoes = InscricaoAtividade.objects.filter(inscricao_evento__participante=request.user).select_related('atividade__evento', 'atividade__sala').order_by('atividade__inicio', 'atividade__titulo')
    eventos = request.user.inscricoes_eventos.select_related('evento').order_by('evento__data_inicio')
    return render(request, 'programacao/agenda.html', {'inscricoes': inscricoes, 'inscricoes_eventos': eventos})


class Painel(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'programacao.view_evento'
    http_method_names = ['get', 'head', 'options']
    model = Evento
    template_name = 'programacao/painel.html'

    def get_queryset(self):
        return Evento.objects.filter(organizador=self.request.user).prefetch_related('atividades__inscricoes__inscricao_evento__participante', 'atividades__sala')


@login_required
def meus_eventos(request):
    if not request.user.has_perm('programacao.add_evento'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, 'programacao/lista.html', {'eventos': request.user.eventos_organizados.all(), 'meus_eventos': True})
