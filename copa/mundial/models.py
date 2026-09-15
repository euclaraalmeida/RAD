from django.db import models


class Grupo(models.Model):
    letra = models.CharField(max_length=1, unique=True)

    class Meta:
        ordering = ["letra"]
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"

    def __str__(self):
        return f"Grupo {self.letra}"


class Estadio(models.Model):
    nome = models.CharField(max_length=100)
    cidade = models.CharField(max_length=60)
    capacidade = models.PositiveIntegerField()

    class Meta:
        ordering = ["nome"]
        verbose_name = "Estádio"
        verbose_name_plural = "Estádios"

    def __str__(self):
        return f"{self.nome} ({self.cidade})"


class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    pais = models.CharField(
        max_length=60,
        verbose_name="País"
    )

    class Meta:
        abstract = True
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.pais})"


class Tecnico(Pessoa):

    class Meta(Pessoa.Meta):
        verbose_name = "Técnico"
        verbose_name_plural = "Técnicos"


class Arbitro(Pessoa):

    class Meta(Pessoa.Meta):
        verbose_name = "Árbitro"
        verbose_name_plural = "Árbitros"


class Selecao(models.Model):
    nome = models.CharField(
        max_length=60,
        unique=True
    )

    sigla = models.CharField(
        max_length=3,
        unique=True,
        help_text="Código FIFA de três letras, como BRA ou ARG",
    )

    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.PROTECT,
        related_name="selecoes",
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Seleção"
        verbose_name_plural = "Seleções"

    def __str__(self):
        return self.nome


class Partida(models.Model):

    class Fase(models.TextChoices):
        GRUPOS = "GR", "Fase de grupos"
        DEZESSEIS_AVOS = "DA", "Dezesseis avos de final"
        OITAVAS = "OI", "Oitavas de final"
        QUARTAS = "QU", "Quartas de final"
        SEMI = "SE", "Semifinal"
        TERCEIRO = "TE", "Disputa do terceiro lugar"
        FINAL = "FI", "Final"

    fase = models.CharField(
        max_length=2,
        choices=Fase.choices,
        default=Fase.GRUPOS,
        verbose_name="Fase",
    )

    grupo = models.ForeignKey(
        Grupo,
        on_delete=models.PROTECT,
        related_name="partidas",
        null=True,
        blank=True,
        help_text="Preencher apenas para partidas da fase de grupos",
    )

    mandante = models.ForeignKey(
        Selecao,
        on_delete=models.PROTECT,
        related_name="partidas_como_mandante",
    )

    visitante = models.ForeignKey(
        Selecao,
        on_delete=models.PROTECT,
        related_name="partidas_como_visitante",
    )

    estadio = models.ForeignKey(
        Estadio,
        on_delete=models.PROTECT,
        related_name="partidas",
        verbose_name="Estádio",
    )

    arbitros = models.ManyToManyField(
        Arbitro,
        related_name="partidas",
        blank=True,
        verbose_name="Árbitros",
    )

    data_hora = models.DateTimeField(
        verbose_name="Data e hora"
    )

    gols_mandante = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    gols_visitante = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    encerrada = models.BooleanField(
        default=False
    )

    registrada_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizada_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["data_hora"]
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"

    def __str__(self):
        return f"{self.mandante} x {self.visitante}"

    def placar(self):
        if not self.encerrada:
            return "a realizar"

        return f"{self.gols_mandante} x {self.gols_visitante}"

    def vencedor(self):
        if not self.encerrada:
            return None

        if self.gols_mandante > self.gols_visitante:
            return self.mandante

        if self.gols_visitante > self.gols_mandante:
            return self.visitante

        return None

    def eliminatoria(self):
        return self.fase != self.Fase.GRUPOS