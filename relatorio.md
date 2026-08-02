# Relatório Completo do Projeto — Finanpy

> Gerado em: 2026-05-18 · Atualizado em: 2026-08-02 (Sprints 8 e 9)

---

## 1. Visão Geral

**Finanpy** é uma aplicação web de gestão financeira pessoal desenvolvida com Django full-stack. Permite ao usuário controlar contas bancárias, categorias de transações e movimentações financeiras, com dashboard de resumo mensal.

| Item | Valor |
|---|---|
| Linguagem | Python 3.13 |
| Framework | Django 6.0.3 |
| Banco de dados | SQLite (db.sqlite3) |
| Frontend | TailwindCSS via CDN + Django Template Language |
| Autenticação | Customizada (e-mail como USERNAME_FIELD) |
| Interface | Português Brasileiro |
| Testes | pytest + pytest-django (94 testes) |
| Containerização | Docker + Docker Compose (Python 3.12-slim) |

---

## 2. Stack Tecnológica

### Dependências (requirements.txt)

```
asgiref==3.11.1
Django==6.0.3
sqlparse==0.5.5
tzdata==2026.1
pytest
pytest-django
```

> O arquivo é gravado em UTF-8 sem BOM — obrigatório para o `pip install` funcionar dentro do container Linux.

### Frontend
- TailwindCSS via CDN (sem build step)
- Fonte Inter via Google Fonts CDN
- JavaScript Vanilla (sem frameworks)
- Tema escuro (dark mode nativo)

### Infraestrutura
- Docker (imagem base `python:3.12-slim`)
- Docker Compose v2 (serviço `web` + volume nomeado `finanpy_db`)

---

## 3. Estrutura de Diretórios

```
pyfinance/
├── core/                            # Configurações globais do Django
│   ├── settings.py                  # Settings principal
│   ├── urls.py                      # URL raiz
│   ├── views.py                     # LandingView, DashboardView
│   ├── wsgi.py
│   ├── asgi.py
│   └── templatetags/
│       ├── __init__.py
│       └── format_filters.py        # Filtros customizados: brl_currency, active_link
│
├── users/                           # Autenticação e model de usuário
│   ├── models.py                    # User (AbstractUser com login por e-mail)
│   ├── managers.py                  # UserManager customizado
│   ├── views.py                     # SignUpView, UserLoginView, UserLogoutView
│   ├── forms.py                     # UserRegistrationForm, EmailAuthenticationForm
│   ├── urls.py                      # signup/, login/, logout/
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
│
├── profiles/                        # Perfil do usuário
│   ├── models.py                    # Profile (OneToOne → User)
│   ├── views.py                     # ProfileUpdateView
│   ├── forms.py                     # UserUpdateForm, ProfileUpdateForm
│   ├── signals.py                   # Cria Profile automaticamente ao criar User
│   ├── urls.py                      # perfil/
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
│
├── accounts/                        # Contas bancárias
│   ├── models.py                    # Account (FK → User; 4 tipos)
│   ├── views.py                     # CRUD completo de contas
│   ├── forms.py                     # AccountForm
│   ├── urls.py                      # contas/*
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
│
├── categories/                      # Categorias de transações
│   ├── models.py                    # Category (FK → User; income/expense)
│   ├── views.py                     # CRUD completo de categorias
│   ├── forms.py                     # CategoryForm
│   ├── signals.py                   # Cria 11 categorias padrão ao criar User
│   ├── urls.py                      # categorias/*
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
│
├── transactions/                    # Transações financeiras
│   ├── models.py                    # Transaction (FK → User, Account, Category)
│   ├── views.py                     # CRUD + filtros + paginação
│   ├── forms.py                     # TransactionForm com validações customizadas
│   ├── signals.py                   # Recalcula saldo da conta em save/delete
│   ├── urls.py                      # transacoes/*
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
│
├── templates/                       # Todos os templates (globais)
│   ├── base.html
│   ├── base_auth.html
│   ├── base_app.html
│   ├── landing.html
│   ├── dashboard.html
│   ├── components/
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── messages.html
│   │   └── modal_confirm.html
│   ├── users/
│   │   ├── signup.html
│   │   └── login.html
│   ├── accounts/
│   │   ├── account_list.html
│   │   ├── account_form.html
│   │   └── account_confirm_delete.html
│   ├── categories/
│   │   ├── category_list.html
│   │   ├── category_form.html
│   │   └── category_confirm_delete.html
│   ├── profiles/
│   │   └── profile_edit.html
│   └── transactions/
│       ├── transaction_list.html
│       ├── transaction_form.html
│       └── transaction_confirm_delete.html
│
├── static/                          # Arquivos estáticos
├── manage.py
├── requirements.txt
├── pytest.ini                       # Configuração do pytest-django
├── conftest.py                      # Fixtures compartilhadas dos testes
├── Dockerfile                       # Imagem da aplicação (Python 3.12-slim)
├── docker-compose.yml               # Serviço web + volume finanpy_db
├── .dockerignore                    # Exclusões do build context
├── CLAUDE.md                        # Guia de desenvolvimento para Claude Code
├── README.md                        # Documentação do projeto
├── TASKS.md                         # Lista de tarefas por sprint
├── PRD.md                           # Product Requirements Document
├── relatorio.md                     # Este relatório
└── db.sqlite3                       # Banco de dados SQLite
```

> Cada app possui seu próprio `tests.py`; o dashboard e os testes de segurança ficam em `core/test_dashboard.py` e `core/test_security.py`.

---

## 4. Configurações Globais (core/settings.py)

| Variável | Valor |
|---|---|
| `AUTH_USER_MODEL` | `'users.User'` |
| `LOGIN_URL` | `'/login/'` |
| `LOGIN_REDIRECT_URL` | `'/dashboard/'` |
| `LOGOUT_REDIRECT_URL` | `'/'` |
| `LANGUAGE_CODE` | `'pt-br'` |
| `TIME_ZONE` | `'America/Sao_Paulo'` |
| `DATABASES` | SQLite — caminho vindo de `DJANGO_DB_PATH` ou `BASE_DIR / 'db.sqlite3'` |
| `SECURE_BROWSER_XSS_FILTER` | `True` |
| `X_CONTENT_TYPE_OPTIONS` | `'nosniff'` |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` |

A variável de ambiente `DJANGO_DB_PATH` permite apontar o SQLite para fora do diretório do projeto (usada pelo Docker para gravar no volume). Quando ausente, o comportamento é o padrão `BASE_DIR / 'db.sqlite3'`.

### INSTALLED_APPS
```
core, accounts, categories, profiles, transactions, users
django.contrib.admin, auth, contenttypes, sessions, messages, staticfiles
```

---

## 5. Modelo de Dados

### Diagrama de Relacionamentos

```
User (AbstractUser)
 ├── Profile           (OneToOne  → User)
 ├── Account           (ForeignKey → User)
 ├── Category          (ForeignKey → User)
 └── Transaction       (ForeignKey → User, Account, Category)
```

### User (`users/models.py`)

| Campo | Tipo | Detalhes |
|---|---|---|
| `email` | `EmailField` | `unique=True`, USERNAME_FIELD |
| `first_name` | `CharField(150)` | obrigatório |
| `last_name` | `CharField(150)` | obrigatório |
| `created_at` | `DateTimeField` | `auto_now_add=True` |
| `updated_at` | `DateTimeField` | `auto_now=True` |

- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = ['first_name', 'last_name']`
- Manager customizado: `UserManager` (create_user, create_superuser)

### Profile (`profiles/models.py`)

| Campo | Tipo | Detalhes |
|---|---|---|
| `user` | `OneToOneField(User)` | `related_name='profile'` |
| `display_name` | `CharField(100)` | `blank=True` |
| `created_at` | `DateTimeField` | `auto_now_add=True` |
| `updated_at` | `DateTimeField` | `auto_now=True` |

### Account (`accounts/models.py`)

| Campo | Tipo | Detalhes |
|---|---|---|
| `user` | `ForeignKey(User)` | `related_name='accounts'` |
| `name` | `CharField(100)` | — |
| `account_type` | `CharField(20)` | choices: checking, savings, wallet, investment |
| `initial_balance` | `DecimalField(10,2)` | `default=0` |
| `current_balance` | `DecimalField(10,2)` | recalculado automaticamente |
| `created_at` | `DateTimeField` | `auto_now_add=True` |
| `updated_at` | `DateTimeField` | `auto_now=True` |

**Tipos de conta:**
- `checking` → Conta Corrente
- `savings` → Poupança
- `wallet` → Carteira
- `investment` → Investimento

**Métodos:**
- `save()` — na criação, seta `current_balance = initial_balance`
- `update_account_balance()` — recalcula `initial_balance + Σ income - Σ expense` via ORM aggregate

### Category (`categories/models.py`)

| Campo | Tipo | Detalhes |
|---|---|---|
| `user` | `ForeignKey(User)` | `related_name='categories'` |
| `name` | `CharField(50)` | — |
| `transaction_type` | `CharField(10)` | choices: income, expense |
| `created_at` | `DateTimeField` | `auto_now_add=True` |
| `updated_at` | `DateTimeField` | `auto_now=True` |

- `unique_together = ['user', 'name', 'transaction_type']`
- `ordering = ['name']`

**Categorias padrão criadas automaticamente (signal):**
- Entrada (4): Salário, Freelance, Investimentos, Outros
- Saída (7): Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros

### Transaction (`transactions/models.py`)

| Campo | Tipo | Detalhes |
|---|---|---|
| `user` | `ForeignKey(User)` | `related_name='transactions'` |
| `account` | `ForeignKey(Account)` | `on_delete=CASCADE` |
| `category` | `ForeignKey(Category)` | `on_delete=PROTECT` |
| `description` | `CharField(200)` | — |
| `amount` | `DecimalField(10,2)` | sempre positivo (validado no form) |
| `transaction_type` | `CharField(10)` | choices: income, expense |
| `date` | `DateField` | — |
| `created_at` | `DateTimeField` | `auto_now_add=True` |
| `updated_at` | `DateTimeField` | `auto_now=True` |

- `ordering = ['-date', '-created_at']`

---

## 6. Views e URLs

### Mapa de URLs Completo

| URL | View | App |
|---|---|---|
| `/` | `LandingView` | core |
| `/dashboard/` | `DashboardView` | core |
| `/signup/` | `SignUpView` | users |
| `/login/` | `UserLoginView` | users |
| `/logout/` | `UserLogoutView` | users |
| `/perfil/` | `ProfileUpdateView` | profiles |
| `/contas/` | `AccountListView` | accounts |
| `/contas/nova/` | `AccountCreateView` | accounts |
| `/contas/<pk>/editar/` | `AccountUpdateView` | accounts |
| `/contas/<pk>/excluir/` | `AccountDeleteView` | accounts |
| `/categorias/` | `CategoryListView` | categories |
| `/categorias/nova/` | `CategoryCreateView` | categories |
| `/categorias/<pk>/editar/` | `CategoryUpdateView` | categories |
| `/categorias/<pk>/excluir/` | `CategoryDeleteView` | categories |
| `/transacoes/` | `TransactionListView` | transactions |
| `/transacoes/nova/` | `TransactionCreateView` | transactions |
| `/transacoes/<pk>/editar/` | `TransactionUpdateView` | transactions |
| `/transacoes/<pk>/excluir/` | `TransactionDeleteView` | transactions |

### Descrição das Views por App

#### `core/views.py`
- **`LandingView(TemplateView)`** — página pública; redireciona usuários autenticados ao dashboard
- **`DashboardView(LoginRequiredMixin, TemplateView)`** — calcula e entrega ao template:
  - `total_balance`: soma de `current_balance` de todas as contas
  - `monthly_income`: soma de entradas do mês corrente
  - `monthly_expense`: soma de saídas do mês corrente
  - `monthly_balance`: income − expense
  - `recent_transactions`: últimas 5 transações
  - `expenses_by_category`: gastos agrupados por categoria (mês corrente)

#### `users/views.py`
- **`SignUpView(CreateView)`** — cadastro com auto-login após registro, redireciona ao dashboard
- **`UserLoginView(LoginView)`** — usa `EmailAuthenticationForm` (login por e-mail)
- **`UserLogoutView(LogoutView)`** — redireciona para `/`

#### `profiles/views.py`
- **`ProfileUpdateView(LoginRequiredMixin, View)`** — GET/POST com dois forms simultâneos (`UserUpdateForm` + `ProfileUpdateForm`)

#### `accounts/views.py`
- **`AccountListView`** — lista filtrada por `user`
- **`AccountCreateView`** — atribui `user = request.user` no `form_valid`
- **`AccountUpdateView`** — não permite editar `initial_balance`; filtra queryset por user
- **`AccountDeleteView`** — filtra queryset por user; mensagem de sucesso

#### `categories/views.py`
- **`CategoryListView`** — lista filtrada por user
- **`CategoryCreateView`** — atribui user no `form_valid`
- **`CategoryUpdateView`** — filtra queryset por user
- **`CategoryDeleteView`** — bloqueia exclusão se existirem transações vinculadas

#### `transactions/views.py`
- **`TransactionListView`** — paginação de 20 por página; filtros via GET:
  - `date_from`, `date_to`, `transaction_type`, `account`, `category`
- **`TransactionCreateView`** — filtra `account`/`category` pelo user via `get_form()`
- **`TransactionUpdateView`** — filtra queryset por user
- **`TransactionDeleteView`** — filtra queryset por user; mensagem de sucesso

---

## 7. Formulários e Validações

### `users/forms.py`
- **`UserRegistrationForm(UserCreationForm)`** — campos: first_name, last_name, email, password1, password2
- **`EmailAuthenticationForm(AuthenticationForm)`** — substitui campo `username` por `email`

### `profiles/forms.py`
- **`UserUpdateForm(ModelForm)`** — campos: first_name, last_name, email
- **`ProfileUpdateForm(ModelForm)`** — campo: display_name

### `accounts/forms.py`
- **`AccountForm(ModelForm)`** — campos: name, account_type, initial_balance
  - Widget de `initial_balance` com `step="0.01"` e `min="0"`

### `categories/forms.py`
- **`CategoryForm(ModelForm)`** — campos: name, transaction_type

### `transactions/forms.py`
- **`TransactionForm(ModelForm)`** — campos: description, amount, date, transaction_type, account, category
  - `__init__`: filtra `account` e `category` pelo user autenticado
  - `clean_amount()`: valida que `amount > 0`
  - `clean()`: valida que `category.transaction_type == transaction_type` (impede mistura)

---

## 8. Signals

| App | Signal | Trigger | Ação |
|---|---|---|---|
| `profiles` | `post_save` | criação de `User` | Cria `Profile` com `display_name = first_name` |
| `categories` | `post_save` | criação de `User` | Cria 11 categorias padrão via `bulk_create` |
| `transactions` | `post_save` | salvar `Transaction` | Chama `account.update_account_balance()` |
| `transactions` | `post_delete` | deletar `Transaction` | Chama `account.update_account_balance()` |

Todos os signals são registrados em `apps.py` via método `ready()`.

---

## 9. Template Tags Customizadas (`core/templatetags/format_filters.py`)

### `brl_currency`
Converte um valor Decimal para o formato monetário brasileiro.
```
{{ valor|brl_currency }}  →  "R$ 1.234,56"
```

### `active_link`
Tag para marcar o item ativo na sidebar/navbar com base na URL atual.
```
{% active_link request 'url_name' 'active_class' 'inactive_class' %}
```

---

## 10. Templates

### Templates Base
| Arquivo | Descrição |
|---|---|
| `base.html` | HTML5 master, TailwindCSS CDN, Inter font, blocos: title, content, extra_js |
| `base_auth.html` | Layout centralizado para login/cadastro (card central) |
| `base_app.html` | Layout com navbar, sidebar desktop, overlay sidebar mobile |

### Componentes
| Arquivo | Descrição |
|---|---|
| `components/navbar.html` | Logo, botão hambúrguer (mobile), nome do usuário, logout |
| `components/sidebar.html` | Links com ícones SVG: Dashboard, Contas, Categorias, Transações, Perfil |
| `components/messages.html` | Mensagens Django com auto-dismiss em 5s (success, error, warning, info) |
| `components/modal_confirm.html` | Modal de confirmação reutilizável para exclusões (JavaScript vanilla) |

### Páginas Públicas
| Arquivo | Descrição |
|---|---|
| `landing.html` | Hero section, features grid, CTA final, footer |

### Autenticação
| Arquivo | Descrição |
|---|---|
| `users/signup.html` | Formulário de cadastro |
| `users/login.html` | Formulário de login por e-mail |

### Páginas da Aplicação
| Arquivo | Descrição |
|---|---|
| `dashboard.html` | 4 cards de resumo + tabela de últimas transações + gastos por categoria |
| `profiles/profile_edit.html` | Edição de perfil (dados do User + Profile) |
| `accounts/account_list.html` | Tabela de contas com saldo, tipo e ações |
| `accounts/account_form.html` | Formulário de criar/editar conta |
| `accounts/account_confirm_delete.html` | Confirmação de exclusão de conta |
| `categories/category_list.html` | Tabela com badges de tipo (verde/vermelho) |
| `categories/category_form.html` | Formulário de criar/editar categoria |
| `categories/category_confirm_delete.html` | Confirmação de exclusão |
| `transactions/transaction_list.html` | Tabela com barra de filtros, paginação (20/pág), modal |
| `transactions/transaction_form.html` | Formulário de criar/editar transação |
| `transactions/transaction_confirm_delete.html` | Confirmação de exclusão |

---

## 11. Design System

### Paleta de Cores

| Papel | Classe Tailwind | Uso |
|---|---|---|
| Background body | `bg-gray-950` | Fundo da página |
| Cards | `bg-gray-900` | Cards, modais |
| Inputs | `bg-gray-800` | Campos de formulário |
| Accent primário | `bg-emerald-500` / `text-emerald-400` | Entradas, botão salvar, itens ativos |
| Perigo | `bg-rose-500` / `text-rose-400` | Exclusão, saídas |
| Accent secundário | `bg-violet-500` / `text-violet-400` | Badges, links |
| Texto principal | `text-gray-100` | Corpo de texto |
| Texto secundário | `text-gray-400` | Labels, subtítulos |

### Componentes UI
- **Botões**: emerald (primário), rose (perigo), gray (secundário/cancelar)
- **Inputs**: fundo `bg-gray-800`, borda `border-gray-700`, foco `ring-emerald-500`
- **Cards**: `bg-gray-900 border border-gray-700 rounded-xl`
- **Tabelas**: linhas alternadas, hover com `hover:bg-gray-800`
- **Badges**: verde para "Entrada", vermelho para "Saída"
- **Paginação**: botões estilizados Previous/Next

---

## 12. Funcionalidades Implementadas

### Autenticação
- [x] Cadastro de usuário (e-mail + nome + senha)
- [x] Login por e-mail (sem username)
- [x] Logout
- [x] Redirecionamento automático de usuários logados na landing page
- [x] Proteção de todas as views com `LoginRequiredMixin`

### Perfil
- [x] Criação automática de Profile via signal ao criar User
- [x] Edição de dados do usuário (nome, e-mail) e perfil (display_name)

### Contas Bancárias
- [x] CRUD completo (criar, listar, editar, excluir)
- [x] 4 tipos de conta (corrente, poupança, carteira, investimento)
- [x] Saldo atual calculado automaticamente a partir das transações
- [x] Saldo inicial setado como saldo atual na criação

### Categorias
- [x] CRUD completo
- [x] 11 categorias padrão criadas automaticamente para cada novo usuário
- [x] Proteção contra exclusão de categorias com transações vinculadas
- [x] Tipos: income (Entrada) e expense (Saída)

### Transações
- [x] CRUD completo
- [x] Validação: valor sempre positivo
- [x] Validação: categoria deve ser do mesmo tipo da transação
- [x] Filtros: por período, tipo, conta e categoria
- [x] Paginação (20 por página)
- [x] Atualização automática do saldo da conta (signal post_save e post_delete)

### Dashboard
- [x] Saldo total de todas as contas
- [x] Entradas do mês corrente
- [x] Saídas do mês corrente
- [x] Balanço mensal (entradas − saídas)
- [x] Últimas 5 transações
- [x] Gastos por categoria (mês corrente)

### UX / Interface
- [x] Design dark (tema escuro)
- [x] Sidebar desktop com ícones SVG
- [x] Menu hambúrguer mobile com overlay
- [x] Modal de confirmação para exclusões (JavaScript vanilla)
- [x] Mensagens de feedback com auto-dismiss em 5s
- [x] Formatação de valores monetários em R$ X.XXX,XX
- [x] Badges coloridos para tipos de transação/categoria
- [x] Estados hover e focus em elementos interativos
- [x] Responsividade (320px a 1440px)

### Segurança
- [x] Todas as queries filtradas por `user=request.user`
- [x] Acesso direto a dados de outro usuário retorna 404
- [x] `{% csrf_token %}` em todos os formulários
- [x] `SECURE_BROWSER_XSS_FILTER = True`
- [x] `X_CONTENT_TYPE_OPTIONS = 'nosniff'`

### Testes
- [x] `pytest` + `pytest-django` configurados (`pytest.ini`)
- [x] Fixtures base compartilhadas em `conftest.py`
- [x] Cobertura de users, profiles, accounts, categories, transactions, dashboard e segurança
- [x] 94 testes passando

### Infraestrutura
- [x] `Dockerfile` com Python 3.12-slim e usuário não-root
- [x] `docker-compose.yml` com serviço web
- [x] Volume nomeado para persistência do banco
- [x] Migrações aplicadas automaticamente na subida do container
- [x] Comandos Docker documentados no README

---

## 13. Execução via Docker

### Arquivos

| Arquivo | Conteúdo |
|---|---|
| `Dockerfile` | Base `python:3.12-slim`; instala `requirements.txt` em camada separada (cache de dependências); cria o usuário não-root `appuser` (uid 1000); expõe a porta 8000 |
| `docker-compose.yml` | Serviço `web` (build local), mapeamento `8000:8000`, volume `finanpy_db` em `/app/data`, `restart: unless-stopped` |
| `.dockerignore` | Exclui `.git`, `.venv`, `__pycache__`, `db.sqlite3` local, `qa_screenshots/` e artefatos de teste do build context |

### Comando de inicialização

```
sh -c "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"
```

As migrações são aplicadas a cada subida do container, antes do servidor iniciar.

### Persistência do banco

O SQLite é gravado em `/app/data/db.sqlite3`, dentro do volume nomeado `finanpy_db`. O caminho vem da variável de ambiente `DJANGO_DB_PATH`, definida no `docker-compose.yml`.

O volume é necessário porque um volume nomeado não pode ser montado sobre um arquivo isolado — apenas sobre um diretório. Os dados sobrevivem a `docker compose down` e a rebuilds da imagem; `docker compose down -v` apaga o banco.

### Comandos principais

```bash
docker compose up --build           # subir (build + migrate + runserver)
docker compose up -d --build        # subir em background
docker compose logs -f web          # acompanhar logs
docker compose down                 # parar (preserva o banco)
docker compose down -v              # parar e apagar o banco
docker compose exec web python manage.py createsuperuser
docker compose exec web pytest      # rodar os testes no container
```

### Resultado da validação (T23.5)

| Verificação | Resultado |
|---|---|
| `docker compose build` | Imagem `pyfinance-web` construída |
| Subida do container | Migrações aplicadas; `System check identified no issues` |
| `GET /` e `GET /login/` | HTTP 200 |
| Arquivo do banco | `/app/data/db.sqlite3` criado, dono `appuser` |
| Persistência | Registro criado sobreviveu a `down` + `up` |
| Suíte de testes no container | 94 testes passando |

> O container roda o `runserver`, adequado a desenvolvimento e avaliação. Para produção seria necessário um servidor WSGI (Gunicorn/uWSGI), `DEBUG = False`, `ALLOWED_HOSTS` configurado e servidor dedicado para estáticos.

---

## 14. Status das Sprints

| Sprint | Tema | Status |
|---|---|---|
| Sprint 1 | Setup e Autenticação | Concluída |
| Sprint 2 | Perfil e Contas Bancárias | Concluída |
| Sprint 3 | Categorias e Categorias Padrão | Concluída |
| Sprint 4 | Transações | Concluída |
| Sprint 5 | Dashboard | Concluída |
| Sprint 6 | Refinamentos e Responsividade | Concluída |
| Sprint 7 | Polimento e Preparação para Produção | Concluída |
| Sprint 8 | Testes | Concluída |
| Sprint 9 | Docker | Concluída |

### Progresso geral: 100% concluído

Todas as tarefas do `TASKS.md` estão marcadas como concluídas.

---

## 15. Convenções do Projeto

| Aspecto | Convenção |
|---|---|
| Linguagem do código | Inglês |
| Interface do usuário | Português Brasileiro |
| Aspas Python | Simples (`'`) |
| Views | Class-based views (CBVs) com `LoginRequiredMixin` |
| Campos de data | `DateTimeField(auto_now_add=True)` e `auto_now=True` em todos os models |
| Valores monetários | `DecimalField(max_digits=10, decimal_places=2)` |
| Segurança de dados | Toda query de listagem filtra por `user=request.user` |
| Saldo de conta | Recalculado via signal a cada criação/edição/exclusão de transação |
| Templates | Globais em `templates/` na raiz (não dentro das apps) |

---

## 16. Arquivos de Documentação

| Arquivo | Conteúdo |
|---|---|
| `README.md` | Descrição, stack, instalação local, execução via Docker, comandos, estrutura, settings configuráveis |
| `CLAUDE.md` | Guia de desenvolvimento para Claude Code: comandos, arquitetura, convenções, design system |
| `TASKS.md` | Lista completa de tarefas por sprint com status de conclusão |
| `PRD.md` | Product Requirements Document com requisitos do produto |
| `relatorio.md` | Este arquivo — relatório completo do projeto |
