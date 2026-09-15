# RELATORIO.md

## 1. Por que `Pessoa` foi declarada como abstrata em vez de virar uma tabela?

`Pessoa` foi declarada como uma classe abstrata porque `Tecnico` e `Arbitro` possuem os mesmos atributos, como `nome` e `pais`. Dessa forma, evita-se repetir os mesmos campos em duas classes diferentes.

Como `Pessoa` possui `abstract = True`, ela não vira uma tabela no banco de dados. Seus campos são herdados pelas classes filhas `Tecnico` e `Arbitro`.

---

## 2. Quantas operações o Django gerou na migration `0002` e por quê?

O Django gerou **duas operações `AddField`**.

Isso aconteceu porque o campo `data_nascimento` foi adicionado à classe abstrata `Pessoa`. Como `Pessoa` não possui tabela própria, o Django adiciona esse campo separadamente nas tabelas das classes filhas:

- `Tecnico`
- `Arbitro`

---

## 3. Por que o `related_name` é obrigatório nas FKs `mandante` e `visitante`?

O `related_name` é obrigatório porque `mandante` e `visitante` são duas `ForeignKey` diferentes apontando para o mesmo model, `Selecao`.

Sem nomes diferentes para a relação inversa, o Django tentaria criar o mesmo caminho reverso para os dois relacionamentos, causando conflito.


## 4. Cole a saída de print(qs.query) para a consulta do Passo 6.8 e aponte os JOIN.


qs = Partida.objects.filter(mandante__grupo__letra="A")
print(qs.query)
SELECT "mundial_partida"."id", "mundial_partida"."fase", "mundial_partida"."grupo_id", "mundial_partida"."mandante_id", "mundial_partida"."visitante_id", "mundial_partida"."estadio_id", "mundial_partida"."data_hora", "mundial_partida"."gols_mandante", "mundial_partida"."gols_visitante", "mundial_partida"."encerrada", "mundial_partida"."registrada_em", "mundial_partida"."atualizada_em" FROM "mundial_partida" INNER JOIN "mundial_selecao" ON ("mundial_partida"."mandante_id" = "mundial_selecao"."id") INNER JOIN "mundial_grupo" ON ("mundial_selecao"."grupo_id" = "mundial_grupo"."id") WHERE "mundial_grupo"."letra" = A ORDER BY "mundial_partida"."data_hora" ASC
