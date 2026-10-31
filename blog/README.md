# Blog IFPB

Projeto das atividades de RAD: laboratório 03, formulários (04) e autenticação/autorização (05). Python 3.13 e Django 5.2, com SQLite e sem bibliotecas extras de formulários ou autenticação.

## Executar no Windows

Abra o PowerShell nesta pasta:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Se o PowerShell bloquear a ativação, utilize diretamente o Python do ambiente, sem mudar a política do computador:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Abra http://127.0.0.1:8000/. O Admin fica em http://127.0.0.1:8000/admin/.

O ambiente e o banco local já estão preparados. As cinco contas estão em `.credenciais-locais.md`, arquivo ignorado pelo Git: `admin`, `redator1`, `redator2`, `editor` e `leitor`. As senhas são individuais e foram geradas apenas para este laboratório.

## Recriar em outra máquina

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Esse procedimento cria um banco vazio. Cadastre categorias, tags e posts pelo Admin. Em Autenticação e Autorização > Grupos, crie Redatores com as permissões de adicionar/alterar post e Editores com adicionar/alterar/excluir post. Associe cada usuário ao grupo apropriado. O cadastro público cria somente leitores sem privilégios.

## Verificar

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

O relatório detalha decisões e verificações de segurança exigidas pela atividade.

## Arquivos locais e entrega

`.venv`, caches, banco, credenciais, `.env` e `backups/` estão ignorados. O banco preenchido existe localmente para a entrega solicitada pelo laboratório 03; não precisa ser versionado para isso. A cópia anterior à autenticação está em `backups/antes-autenticacao.zip`.

Nada foi enviado ao GitHub. A pasta recebida não possui metadados `.git`; a configuração do remoto e o envio serão tratados depois.
