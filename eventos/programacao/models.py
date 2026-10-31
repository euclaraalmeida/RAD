from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Sala(models.Model):
    nome = models.CharField('nome', max_length=100, unique=True)
    bloco = models.CharField('bloco', max_length=80)
    capacidade = models.PositiveIntegerField('capacidade', validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['nome']
        constraints = [models.CheckConstraint(condition=models.Q(capacidade__gte=1), name='sala_capacidade_positiva')]

    def __str__(self):
        return f'{self.nome} — {self.bloco}'

    def clean(self):
        super().clean()
        if self.pk and self.capacidade is not None:
            if self.atividades.annotate(total=models.Count('inscricoes')).filter(total__gt=self.capacidade).exists():
                raise ValidationError({'capacidade': 'A capacidade não pode ficar menor que o total de inscritos.'})


class Evento(models.Model):
    nome = models.CharField('nome', max_length=150)
    descricao = models.TextField('descrição')
    data_inicio = models.DateField('data de início')
    data_fim = models.DateField('data de fim')
    inscricoes_abertas = models.BooleanField('inscrições abertas', default=True)
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='eventos_organizados')

    class Meta:
        ordering = ['data_inicio', 'nome']
        constraints = [models.CheckConstraint(condition=models.Q(data_fim__gte=models.F('data_inicio')), name='evento_periodo_valido')]

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('programacao:detalhe', args=[self.pk])

    def clean(self):
        super().clean()
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError({'data_fim': 'O fim do evento não pode vir antes do início.'})
            if self.pk and self.atividades.filter(models.Q(inicio__date__lt=self.data_inicio) | models.Q(fim__date__gt=self.data_fim)).exists():
                raise ValidationError('O novo período deixaria atividades fora do evento.')


class Atividade(models.Model):
    class Tipo(models.TextChoices):
        PALESTRA = 'PA', 'Palestra'
        TREINAMENTO = 'TR', 'Treinamento'
        APRESENTACAO = 'AP', 'Apresentação'

    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='atividades')
    titulo = models.CharField('título', max_length=150)
    tipo = models.CharField('tipo', max_length=2, choices=Tipo.choices)
    descricao = models.TextField('descrição')
    responsavel = models.CharField('responsável', max_length=120)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name='atividades')
    inicio = models.DateTimeField('início')
    fim = models.DateTimeField('fim')

    class Meta:
        ordering = ['inicio', 'titulo']
        constraints = [models.CheckConstraint(condition=models.Q(fim__gt=models.F('inicio')), name='atividade_intervalo_valido')]

    def __str__(self):
        return self.titulo

    @property
    def vagas_restantes(self):
        return max(0, self.sala.capacidade - self.inscricoes.count())

    def clean(self):
        super().clean()
        if not (self.inicio and self.fim):
            return
        if self.fim <= self.inicio:
            raise ValidationError({'fim': 'O fim deve ser posterior ao início.'})
        if self.evento_id:
            inicio = timezone.localtime(self.inicio).date()
            fim = timezone.localtime(self.fim).date()
            if inicio < self.evento.data_inicio or fim > self.evento.data_fim:
                raise ValidationError('A atividade precisa acontecer dentro do período do evento.')
        if self.sala_id:
            conflito = Atividade.objects.exclude(pk=self.pk).filter(sala_id=self.sala_id, inicio__lt=self.fim, fim__gt=self.inicio)
            if conflito.exists():
                raise ValidationError('A sala já está ocupada nesse horário, inclusive em outro evento.')
        if self.pk:
            if self.inscricoes.exclude(inscricao_evento__evento_id=self.evento_id).exists():
                raise ValidationError('Não é possível mudar o evento de uma atividade com inscritos.')
            if self.sala_id and self.inscricoes.count() > self.sala.capacidade:
                raise ValidationError('A sala escolhida não comporta os participantes já inscritos.')
            participantes = self.inscricoes.values_list('inscricao_evento__participante_id', flat=True)
            if InscricaoAtividade.objects.filter(inscricao_evento__participante_id__in=participantes, atividade__inicio__lt=self.fim, atividade__fim__gt=self.inicio).exclude(atividade_id=self.pk).exists():
                raise ValidationError('Esse horário conflita com a agenda de um participante já inscrito.')


class InscricaoEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscricoes')
    participante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscricoes_eventos')
    data = models.DateTimeField('data de inscrição', auto_now_add=True)

    class Meta:
        verbose_name = 'inscrição no evento'
        verbose_name_plural = 'inscrições nos eventos'
        constraints = [models.UniqueConstraint(fields=['evento', 'participante'], name='inscricao_evento_unica')]

    def __str__(self):
        return f'{self.participante} — {self.evento}'

    def clean(self):
        super().clean()
        if self.evento_id and not self.pk and not self.evento.inscricoes_abertas:
            raise ValidationError('As inscrições deste evento estão fechadas.')
        if self.pk:
            antigo = type(self).objects.get(pk=self.pk)
            if antigo.evento_id != self.evento_id or antigo.participante_id != self.participante_id:
                raise ValidationError('Cancele a inscrição e crie outra para mudar evento ou participante.')


class InscricaoAtividade(models.Model):
    inscricao_evento = models.ForeignKey(InscricaoEvento, on_delete=models.CASCADE, related_name='inscricoes_atividades')
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='inscricoes')
    data = models.DateTimeField('data de inscrição', auto_now_add=True)

    class Meta:
        verbose_name = 'inscrição em atividade'
        verbose_name_plural = 'inscrições em atividades'
        ordering = ['atividade__inicio']
        constraints = [models.UniqueConstraint(fields=['inscricao_evento', 'atividade'], name='inscricao_atividade_unica')]

    def __str__(self):
        return f'{self.inscricao_evento.participante} — {self.atividade}'

    def clean(self):
        super().clean()
        if not (self.inscricao_evento_id and self.atividade_id):
            return
        if self.inscricao_evento.evento_id != self.atividade.evento_id:
            raise ValidationError('É necessário estar inscrito no evento desta atividade.')
        if not self.pk and not self.atividade.evento.inscricoes_abertas:
            raise ValidationError('As inscrições deste evento estão fechadas.')
        outras = InscricaoAtividade.objects.exclude(pk=self.pk)
        if outras.filter(atividade_id=self.atividade_id).count() >= self.atividade.sala.capacidade:
            raise ValidationError('Esta atividade está lotada.')
        if outras.filter(inscricao_evento__participante_id=self.inscricao_evento.participante_id, atividade__inicio__lt=self.atividade.fim, atividade__fim__gt=self.atividade.inicio).exists():
            raise ValidationError('Esta atividade conflita com outra da sua agenda, inclusive em outro evento.')
