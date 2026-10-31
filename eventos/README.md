# Inscrições em eventos do campus

Atividade de ponto extra de Rapid Application Development — IFPB.

**Integrante:** Maria Clara. **Modalidade:** individual.

## Executar

O projeto usa Python 3.13, Django 5.2 e SQLite. O ambiente virtual local já está criado e as migrations estão aplicadas.

Abra o PowerShell na pasta `eventos`:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Se não quiser ativar o ambiente, execute diretamente:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Abra [o sistema](http://127.0.0.1:8000/) ou [o Admin](http://127.0.0.1:8000/admin/). Os dois projetos do repositório são independentes: execute o comando dentro de `eventos`, não de `blog`.

Para instalar em outra máquina, preservando o banco que acompanha a entrega:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## Cinco contas de avaliação

Credenciais exclusivas do banco de demonstração desta atividade:

| Usuário | Senha | Papel |
| --- | --- | --- |
| admin | CampusAdmin!2026 | Superusuário; cadastra salas pelo Admin |
| organizador1 | CampusOrgUm!2026 | Organizador da Semana de Tecnologia |
| organizador2 | CampusOrgDois!2026 | Organizador da Jornada de Pesquisa |
| participante1 | CampusPartUm!2026 | Participante comum |
| participante2 | CampusPartDois!2026 | Participante comum; permite ocupar a segunda vaga |

Os organizadores pertencem ao grupo `Organizadores`, com as permissões de visualizar, adicionar, alterar e excluir eventos e atividades. As contas de participantes foram criadas pelo cadastro público e não têm grupos nem permissões administrativas. Uma nova conta também é participante comum. Após se cadastrar, entre pela tela de login.

## Dados cadastrados

Todos os horários abaixo estão no fuso `America/Fortaleza` (UTC−3).

### Salas

| Sala | Bloco | Capacidade |
| --- | --- | ---: |
| Sala de estudos | Bloco A | **2** |
| Auditório | Bloco B | 80 |
| Laboratório de informática | Bloco C | 25 |

### Eventos

| Evento | Período | Organizador | Inscrições |
| --- | --- | --- | --- |
| Semana de Tecnologia | 23 a 25/11/2026 | organizador1 | Abertas |
| Jornada de Pesquisa | 24 a 26/11/2026 | organizador2 | Abertas |

Os períodos se cruzam em 24 e 25 de novembro.

### Atividades

| Atividade | Evento | Tipo | Responsável | Sala | Horário |
| --- | --- | --- | --- | --- | --- |
| Oficina de Python | Semana de Tecnologia | Treinamento | Ana Silva | Sala de estudos | 24/11, 09h–10h |
| Pesquisa e inovação no campus | Jornada de Pesquisa | Palestra | Bruno Costa | Auditório | 24/11, 09h–10h |
| Primeiros passos com Django | Semana de Tecnologia | Treinamento | Carla Santos | Sala de estudos | 24/11, 10h–11h |
| Desenvolvimento web na prática | Semana de Tecnologia | Palestra | Diego Lima | Laboratório de informática | 24/11, 09h30–10h30 |
| Mostra de projetos de pesquisa | Jornada de Pesquisa | Apresentação | Elisa Souza | Auditório | 25/11, 14h–15h |

A Oficina de Python e Pesquisa e inovação são simultâneas em eventos diferentes, mas usam salas diferentes. Um participante não pode escolher ambas. Desenvolvimento web também conflita com a Oficina e com Primeiros passos com Django dentro da Semana. A Oficina e Primeiros passos usam a mesma sala em horários consecutivos, portanto podem coexistir e podem ser escolhidas pelo mesmo participante.

O banco inicia sem inscrições, com todas as vagas livres, para reproduzir os passos de avaliação. Não há registros temporários de verificação.

## Como demonstrar

1. Abra a lista e uma programação sem login: atividades, salas e vagas são públicas.
2. Entre como participante1, inscreva-se na Semana e na Oficina: a sala passa de duas para uma vaga.
3. Entre como participante2 e repita: a Oficina fica lotada e o botão desaparece. Um organizador também é usuário autenticado; pode ser a terceira conta para verificar a recusa de uma inscrição adicional por POST.
4. Como participante1, inscreva-se também na Jornada. Pesquisa e inovação não será oferecida, pois conflita com a Oficina. A rota também recusa a inscrição se chamada diretamente.
5. Cancele a Oficina na Minha agenda: uma vaga volta imediatamente e a inscrição na Semana permanece. Cancelar a Semana remove junto todas as inscrições nas atividades dela.
6. Como organizador1, abra Meus eventos e o painel da Semana. Apenas ele pode editar seus eventos e atividades e consultar os respectivos inscritos. Organizador2 recebe 404 ao tentar acessar esses endereços diretamente.
7. Para verificar inscrições fechadas, edite temporariamente o evento como seu organizador e desmarque Inscrições abertas. Novas inscrições no evento e nas atividades serão recusadas; os cancelamentos continuam disponíveis.

## Modelagem e regras

São cinco entidades: `Sala`, `Evento`, `Atividade`, `InscricaoEvento` e `InscricaoAtividade`. A inscrição em atividade aponta para a inscrição no evento, que identifica o participante. Essa relação permite cancelar o evento com exclusão em cascata de todas as escolhas daquele participante.

Categoria de exclusão: organizador e sala usados ficam protegidos por `PROTECT`; excluir evento remove suas atividades e inscrições por `CASCADE`. Unicidade de evento/participante e inscrição/atividade é garantida também no banco. Capacidade mínima e ordem das datas têm restrições de banco.

Intervalos são tratados como início incluído e fim excluído. A regra de sobreposição é `inicio_existente < fim_novo` **e** `fim_existente > inicio_novo`, cobrindo inclusive intervalos que contêm o outro inteiro. A agenda consulta todas as inscrições do participante, sem limitar ao evento atual; a ocupação de sala também considera todos os eventos.

Os models validam período do evento, horário, ocupação, capacidade, evento correspondente e conflitos. As operações de inscrição consultam o banco dentro de `transaction.atomic()`. O SQLite está configurado com `transaction_mode=IMMEDIATE`: a transação de escrita obtém o bloqueio antes de consultar e gravar, para que requisições concorrentes não usem a mesma última vaga. As telas de alteração de atividades também executam validação e gravação em transação. As vagas são sempre calculadas com a capacidade da sala menos o total atual de inscrições.

Mudanças de horário de atividades com inscritos são recusadas se criarem conflitos para esses participantes. Trocar para sala menor ou reduzir sua capacidade não pode deixar inscrições acima do limite. Alterar o período do evento não pode deixar atividades fora dele.

Login e logout usam as views nativas do Django. O cadastro usa `CreateView` com `UserCreationForm`, sem implementar uma view de autenticação. Todas as alterações são feitas por POST, com CSRF e redirecionamento. GET em exclusão apenas mostra a confirmação. Há proteção por decoradores nas inscrições e por mixins no CRUD e no painel. As rotas conferem permissões e propriedade, independentemente dos botões. Nenhuma view usa `is_superuser` como regra de autorização.

## Verificação e pendências

Os **27 critérios de aceitação** foram exercitados pelo cliente HTTP do Django em banco separado, agrupados em 13 verificações que passaram. Também foram conferidos CSRF, exclusão somente por POST, intervalos contidos e horários consecutivos. Os scripts temporários de verificação não fazem parte da pasta entregue. A listagem e a programação públicas também foram abertas no navegador.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

**Requisitos obrigatórios pendentes:** nenhum. **Desafio opcional de lista de espera:** não implementado.

O `db.sqlite3` acompanha o projeto por exigência expressa da atividade. `.venv`, caches e configurações locais ficam ignorados pelo Git. O banco contém somente as contas e dados de demonstração descritos acima.

Referências: [autenticação do Django](https://docs.djangoproject.com/en/5.2/topics/auth/default/) e [SQLite e transações](https://docs.djangoproject.com/en/5.2/ref/databases/#sqlite-notes).
