# Finanpy

Sistema de controle de finanças pessoais desenvolvido com Django. Permite gerenciar contas bancárias, categorias e transações financeiras com atualização automática de saldos, dashboard com resumo mensal e interface responsiva em tema escuro.

---

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.13 + Django 6.0 |
| Banco de dados | SQLite (desenvolvimento) |
| Frontend | TailwindCSS via CDN |
| Autenticação | Django Auth com e-mail como campo de login |
| Templates | Django Template Language (DTL) |

---

## Pré-requisitos

- Python 3.12 ou superior
- pip

---

## Instalação e setup local

**1. Clone o repositório**

```bash
git clone <url-do-repositorio>
cd pyfinance
```

**2. Crie e ative o ambiente virtual**

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Execute as migrações**

```bash
python manage.py migrate
```

**5. Crie um superusuário**

```bash
python manage.py createsuperuser
```

> O campo de login é **e-mail**, não username. Informe e-mail, primeiro nome, último nome e senha.

**6. Inicie o servidor de desenvolvimento**

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

---

## Executando com Docker

Alternativa ao setup local — não requer Python nem virtualenv na máquina, apenas Docker.

**Pré-requisitos:** Docker Engine 24+ e Docker Compose v2.

**1. Suba a aplicação**

```bash
docker compose up --build
```

O container aplica as migrações automaticamente na inicialização e sobe o servidor de desenvolvimento. Acesse `http://localhost:8000/`.

**2. Crie um superusuário** (em outro terminal, com o container rodando)

```bash
docker compose exec web python manage.py createsuperuser
```

### Comandos Docker úteis

```bash
# Subir em background
docker compose up -d --build

# Ver logs
docker compose logs -f web

# Parar os containers (o banco é preservado no volume)
docker compose down

# Parar e APAGAR o banco de dados
docker compose down -v

# Rodar comandos do manage.py dentro do container
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell

# Rodar os testes dentro do container
docker compose exec web pytest

# Abrir um shell no container
docker compose exec web sh

# Reconstruir a imagem após alterar o requirements.txt
docker compose build --no-cache
```

### Persistência do banco de dados

O SQLite fica no volume nomeado `finanpy_db`, montado em `/app/data` dentro do container. O caminho do arquivo é definido pela variável de ambiente `DJANGO_DB_PATH` (`/app/data/db.sqlite3` no compose).

Isso mantém o banco intacto entre `docker compose down` / `up` e entre rebuilds da imagem. Para apagar os dados, use `docker compose down -v`.

Fora do Docker, `DJANGO_DB_PATH` não é definida e o Django usa `BASE_DIR / 'db.sqlite3'` como sempre — o setup local não muda.

> O container roda `runserver`, adequado para desenvolvimento e avaliação. Para produção, troque por um servidor WSGI (Gunicorn/uWSGI), defina `DEBUG = False`, configure `ALLOWED_HOSTS` e sirva os estáticos por um servidor dedicado.

---

## Comandos úteis

```bash
# Iniciar servidor de desenvolvimento
python manage.py runserver

# Criar migrações após alterar models
python manage.py makemigrations

# Aplicar migrações pendentes
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Abrir shell Django
python manage.py shell

# Rodar todos os testes
python manage.py test

# Rodar testes de um app específico
python manage.py test users
python manage.py test accounts
python manage.py test categories
python manage.py test transactions
```

---

## Estrutura de diretórios

```
pyfinance/
├── core/                   # Configuração global (settings, urls, wsgi, asgi)
│   ├── settings.py
│   ├── urls.py
│   ├── views.py            # DashboardView
│   └── templatetags/       # Filtros customizados (brl_currency, active_link)
├── users/                  # Model de usuário customizado (login via e-mail)
├── profiles/               # Perfil do usuário (criado via signal post_save)
├── accounts/               # Contas bancárias
├── categories/             # Categorias de transações (padrão criadas via signal)
├── transactions/           # Transações financeiras
├── templates/              # Templates globais (raiz do projeto)
│   ├── base.html
│   ├── base_auth.html
│   ├── base_app.html
│   ├── dashboard.html
│   ├── landing.html
│   ├── components/         # Navbar, sidebar, messages, modal
│   ├── accounts/
│   ├── categories/
│   ├── profiles/
│   ├── transactions/
│   └── users/
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
├── manage.py
├── requirements.txt
├── Dockerfile              # Imagem da aplicação (Python 3.12 slim)
├── docker-compose.yml      # Serviço web + volume de persistência do banco
└── db.sqlite3              # Banco de dados SQLite (gerado após migrate)
```

---

## Variáveis de settings configuráveis

Todas as variáveis abaixo estão em `core/settings.py`.

| Variável | Valor padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | string gerada | Chave secreta do Django. **Obrigatório trocar em produção.** |
| `DEBUG` | `True` | Modo debug. Defina `False` em produção. |
| `ALLOWED_HOSTS` | `[]` | Lista de hosts permitidos. Em produção, adicione o domínio da aplicação. |
| `DATABASES` | SQLite (`db.sqlite3`) | Configuração do banco de dados. Troque por PostgreSQL em produção. |
| `DJANGO_DB_PATH` | não definida | Variável de ambiente com o caminho do arquivo SQLite. Se ausente, usa `BASE_DIR / 'db.sqlite3'`. Usada pelo Docker para apontar ao volume. |
| `LANGUAGE_CODE` | `'pt-br'` | Idioma da interface de administração e mensagens do Django. |
| `TIME_ZONE` | `'America/Sao_Paulo'` | Fuso horário usado em datas e horas. |
| `USE_TZ` | `True` | Armazenar datas com timezone no banco. |
| `STATIC_URL` | `'static/'` | URL base para arquivos estáticos. |
| `STATICFILES_DIRS` | `[BASE_DIR / 'static']` | Diretórios adicionais de arquivos estáticos. |
| `AUTH_USER_MODEL` | `'users.User'` | Model de usuário customizado. Não alterar após a primeira migration. |
| `LOGIN_URL` | `'/login/'` | URL de redirecionamento para usuários não autenticados. |
| `LOGIN_REDIRECT_URL` | `'/dashboard/'` | URL de redirecionamento após login bem-sucedido. |
| `LOGOUT_REDIRECT_URL` | `'/'` | URL de redirecionamento após logout. |
| `SECURE_BROWSER_XSS_FILTER` | `True` | Ativa header de proteção XSS no navegador. |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | Impede sniffing de MIME type pelo navegador. |

### Configuração mínima para produção

```python
SECRET_KEY = 'sua-chave-secreta-longa-e-aleatoria'
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finanpy',
        'USER': 'usuario',
        'PASSWORD': 'senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Modelo de dados

```
User (AbstractUser — login via e-mail)
 ├── Profile (OneToOne — criado automaticamente via signal)
 ├── Account (FK) — tipos: Conta Corrente, Poupança, Carteira, Investimento
 ├── Category (FK) — tipos: Entrada, Saída; categorias padrão criadas via signal
 └── Transaction (FK) → também FK para Account e Category
```

Ao criar ou excluir uma `Transaction`, o `current_balance` da `Account` associada é recalculado automaticamente.

Ao criar um novo usuário, as seguintes categorias padrão são criadas automaticamente:

- **Entrada:** Salário, Freelance, Investimentos, Outros
- **Saída:** Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros
