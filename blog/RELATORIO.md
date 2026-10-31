# Relatório das atividades 03, 04 e 05

## Execução e escopo

O projeto foi criado em `blog`, ao lado de `copa` e `enquetes`, com `python -m venv .venv`, instalação de `django==5.2.*`, `startproject config .` e `startapp artigos`. As versões instaladas foram registradas com `pip freeze` em `requirements.txt`. O Python do ambiente virtual foi invocado diretamente nos comandos: isso utiliza o ambiente mesmo sem ativar o prompt do PowerShell.

Foram criadas e aplicadas as migrations e inspecionado o SQL de `0001`: há `categoria_id`, tabela intermediária `artigos_post_tags` e restrições únicas nos slugs. A consulta `Post.objects.filter(categoria__slug='python').query` produziu `INNER JOIN` com a tabela de categorias.

Os cadastros iniciais foram enviados às views reais do Django Admin com o cliente HTTP de testes do Django, autenticado como administrador. Não foram realizados cliques manuais em navegador. Foram cadastradas três categorias (Python, Django e Banco de Dados), cinco tags e seis posts com textos em parágrafos e duas tags cada: quatro publicados e dois rascunhos. Um publicado legado ficou sem resumo para demonstrar o fallback exigido no laboratório 03. Novas publicações pelo formulário da atividade 04 exigem resumo.

Antes de acrescentar autenticação, foi criada a cópia local `backups/antes-autenticacao.zip`. A aplicação final incorpora as três etapas; as permissões da atividade 05 substituem intencionalmente a escrita anônima permitida na etapa 04. Não foram feitos commits, configuração de remoto ou envio ao GitHub.

## Laboratório 03

1. **Por que repetir artigos em artigos/templates/artigos?** A primeira pasta identifica o aplicativo; `templates` é o diretório descoberto pelo Django; o segundo `artigos` cria um namespace para não colidir com templates de outros aplicativos.
2. **Onde os rascunhos são impedidos?** As views de listagem, categoria e busca filtram `situacao=PUBLICADO`. A view de detalhe também restringe a consulta: um visitante não consegue contornar a listagem digitando o slug. Na versão final, somente o próprio autor pode abrir o detalhe de seu rascunho; outros visitantes recebem 404. A área `meus_posts` lista exclusivamente os registros do usuário atual, inclusive rascunhos.
3. **Por que timezone.now sem parênteses?** O campo recebe uma função que será executada para cada novo objeto, em vez de uma data calculada durante a importação do arquivo.
4. **Como o template de lista é reutilizado?** As views entregam `posts` e, quando aplicável, `categoria` ou `meus_posts`. O template usa condicionais para o cabeçalho e o mesmo parcial para os cartões.
5. **O que habilita Ver no site?** O método `Post.get_absolute_url()`, que usa o nome de rota `artigos:detalhe` e o slug do registro.

## Atividade 04: formulários

`PostForm` herda de `ModelForm` e declara explicitamente título, resumo, conteúdo, categoria, tags e situação. Conteúdo usa `Textarea` com 12 linhas. Slug e autor não podem ser escolhidos pelo formulário. `slugify` gera o identificador; colisões sequenciais recebem sufixos `-2`, `-3` etc. Na edição, o slug existente é preservado para manter os links.

`clean_titulo` exige ao menos dez caracteres. `clean` exige resumo para situação Publicado e produz erro geral. Os dados inválidos permanecem no formulário vinculado. Após salvar com `commit=False`, a view cria o objeto e chama `save_m2m()` para persistir as tags.

A criação é uma função porque a atribuição de autoria fica explícita e curta. A edição é uma classe `UpdateView` porque reaproveita o carregamento da instância, o preenchimento e o redirecionamento já fornecidos pelo Django. As duas usam o mesmo formulário e template.

A busca usa `forms.Form`, sem model, com `cleaned_data` e uma consulta `Q` para título OU conteúdo. GET é adequado porque consultar não altera o banco, permite favoritar/compartilhar a URL e repetir a busca sem reenviar uma operação de gravação.

POSTs bem-sucedidos redirecionam (padrão Post/Redirect/Get). Criação, edição e exclusão geram mensagens renderizadas no template base. A confirmação de exclusão por GET não apaga registros; somente POST apaga. Todo formulário POST inclui CSRF. Os links usam nomes de rota.

### Segurança: CSRF

O teste automatizado usa `Client(enforce_csrf_checks=True)`: um POST autenticado sem token retorna **403**, com página de falha de verificação CSRF. O mesmo envio com token válido retorna **302**. Também foi removida temporariamente a tag `{% csrf_token %}` do template de post, carregada a tela e enviado um POST sem token: o servidor retornou **403**. O arquivo original foi restaurado em um bloco `finally` e a presença da tag foi conferida. A recusa ocorre porque falta a prova de que o formulário foi emitido para aquela sessão/origem, protegendo contra requisições forjadas.

## Atividade 05: autenticação e autorização

### Autoria e migração dos registros existentes

`Post.autor` é obrigatório, tem `on_delete=PROTECT` e `related_name='posts'`. Assim `post.autor` e `usuario.posts.all()` funcionam, e excluir usuário com posts gera `ProtectedError`.

A migration `0002` primeiro adiciona autor aceitando nulo, depois atribui os registros antigos ao primeiro usuário staff e finalmente torna a coluna obrigatória. Se não existir staff, cria um autor legado inativo, com senha inutilizável. Isso evita um ID fixo que poderia não existir em outro banco. Usa modelos históricos e o alias da conexão da migration.

No banco local os seis registros permaneceram após aplicar `0002`, inicialmente atribuídos ao administrador. Depois foram distribuídos explicitamente entre os dois redatores e o editor para testar os papéis. Um teste de regressão migra um banco com post sem autor de `0001` para `0002` e verifica preservação do conteúdo e atribuição de autor.

### Contas e grupos

As cinco contas locais são `admin` (superusuário), `redator1` e `redator2` (Redatores), `editor` (Editores) e `leitor` (sem grupo). Os grupos e vínculos foram configurados por requisições às telas do Admin. Redatores recebem `add_post` e `change_post`; Editores também recebem `delete_post`. As senhas foram geradas individualmente, guardadas somente no arquivo local ignorado e aplicadas pelas APIs de criação de usuário.

A conta leitor foi criada por POST à tela pública `/cadastro/`, usando `UserCreationForm`. Foi conferida a sessão iniciada automaticamente e a ausência de grupos/permissões. O cadastro público não concede privilégios nem acesso de staff.

### Login, logout e troca de senha

As rotas de `django.contrib.auth.urls` fornecem as views prontas, com templates em `templates/registration`. `LOGIN_URL`, `LOGIN_REDIRECT_URL` e `LOGOUT_REDIRECT_URL` definem os destinos. O campo oculto `next` preserva a URL pretendida após o login. Logout usa formulário POST com CSRF: o Django 5.2 não permite logout por GET, que retorna 405. A troca de senha usa a view nativa, exige a senha atual e aplica os validadores configurados.

### Proteção das rotas e da interface

A criação e a exclusão usam `login_required` por fora de `permission_required(..., raise_exception=True)`. Anônimos são enviados ao login com `next`; autenticados sem a permissão recebem **403**, pois autenticar novamente não resolveria a falta de autorização.

A edição usa `LoginRequiredMixin` e `PermissionRequiredMixin`, além de `get_queryset()` filtrando pelo usuário atual. A exclusão filtra o objeto pelo autor. Foi escolhido **404 para posts alheios**, pois evita confirmar a existência de registros que aquela pessoa não pode administrar. Nenhuma view usa `is_superuser` para autorizar.

A navegação consulta as permissões e a autoria: criar aparece só para quem pode adicionar; editar e excluir aparecem só para o autor com a respectiva permissão. As views fazem as mesmas verificações independentemente da interface. O detalhe identifica o autor.

### Teste A: acesso direto a registro alheio

Nos testes, o segundo redator abre a página pública do post de outro autor e não vê Editar. Em seguida acessa diretamente a rota de edição: a resposta é **404**, exibindo Página não encontrada com `DEBUG=False`. O bloqueio é o filtro `Post.objects.filter(autor=self.request.user)` em `EditarPost.get_queryset()`. POST direto também retorna 404. Um editor tentando excluir post alheio igualmente recebe 404; um redator tentando excluir o próprio recebe 403 por não ter `delete_post`.

### Teste B: armazenamento de senha

Foi validado que a senha é verificável com `check_password`, mas não aparece em texto puro. O formato padrão é `pbkdf2_sha256$iterações$salt$hash`: quatro partes, indicando algoritmo, quantidade de repetições, valor aleatório por senha e resultado da derivação. O hash não é criptografia reversível e não guarda uma chave para recuperar o original; tentativas de adivinhação ainda são possíveis, por isso os validadores e o custo das iterações são relevantes. Nenhuma senha é atribuída diretamente ao campo do model; o autor legado recebe apenas o marcador de senha inutilizável.

## Verificações

Durante a implementação, uma suíte automatizada temporária verificou validações, dados mantidos após erros, tags, slugs repetidos, criação/edição/exclusão, redirecionamentos e mensagens, ausência de duplicação após GET, busca, categorias, lista vazia, rascunhos, cadastro, login com next, privilégios, autoria, CSRF, troca de senha, logout, proteção das relações e migração de posts antigos. Foram utilizados usuários comuns com grupos, sem depender do superusuário para provar as regras. Após a verificação, a suíte extra e os scripts auxiliares foram removidos a pedido do usuário; os resultados exigidos pelos enunciados foram mantidos neste relatório.

Resultado final: **12 testes aprovados**; `manage.py check` sem problemas; `makemigrations --check --dry-run` sem alterações pendentes. Banco local conferido com seis posts, quatro publicados, dois rascunhos e nenhum autor nulo. Senha local inspecionada: algoritmo `pbkdf2_sha256`, quatro partes.

As verificações HTTP são automatizadas pelo cliente Django. Não se afirma uma conferência manual de todas as telas no navegador.

## Referências consultadas

- https://docs.djangoproject.com/en/5.2/topics/auth/default/
- Código instalado do Django 5.2 para ModelForm, autenticação e validação.

Os enunciados definiram os requisitos; a autorização de execução local e a decisão de deixar o GitHub para depois vieram do pedido do usuário.
