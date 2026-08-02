# Relatório Completo do Projeto — Finanpy

> Gerado em: 2026-05-18 · Atualizado em: 2026-08-02 (Sprint 8 — Agente de IA — concluída)

---

## 1. Visão Geral

**Finanpy** é uma aplicação web de gestão financeira pessoal desenvolvida com Django full-stack. Permite ao usuário controlar contas bancárias, categorias de transações e movimentações financeiras, com dashboard de resumo mensal e análise automatizada das finanças por um agente de IA.

| Item | Valor |
|---|---|
| Linguagem | Python 3.13 |
| Framework | Django 6.0.3 |
| Banco de dados | SQLite (db.sqlite3) |
| Frontend | TailwindCSS via CDN + Django Template Language |
| Autenticação | Customizada (e-mail como USERNAME_FIELD) |
| Agente de IA | LangChain 1.0 + DeepSeek (app `ai`) |
| Interface | Português Brasileiro |
| Testes | pytest + pytest-django (169 testes) |
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
langchain==1.3.14
langchain-deepseek==1.1.0
python-dotenv==1.2.2
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
├── ai/                              # Agente de análise financeira
│   ├── models.py                    # AIAnalysis (FK → User) + manager
│   ├── tools.py                     # build_tools(user) — 7 tools de leitura
│   ├── prompts.py                   # System prompt do consultor financeiro (PT-BR)
│   ├── schemas.py                   # FinancialAnalysis (Pydantic)
│   ├── agent.py                     # build_finance_agent(user) + ChatDeepSeek
│   ├── services.py                  # run_analysis_for_user(user) e cooldown
│   ├── views.py                     # Histórico, detalhe e geração (POST)
│   ├── urls.py                      # analises/*
│   ├── admin.py
│   ├── apps.py
│   ├── management/commands/
│   │   └── run_ai_analysis.py       # Geração em lote
│   ├── test_tools.py                # Valores das tools + isolamento por usuário
│   ├── test_services.py
│   ├── test_views.py
│   ├── test_commands.py
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
│   │   ├── modal_confirm.html
│   │   ├── ai_insight_card.html     # Card da última análise no dashboard
│   │   └── ai_generate_form.html    # Botão de geração + estado de carregamento
│   ├── ai/
│   │   ├── analysis_list.html
│   │   └── analysis_detail.html
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
├── .env.example                     # Chaves esperadas no .env (sem valores reais)
├── pytest.ini                       # Configuração do pytest-django
├── conftest.py                      # Fixtures compartilhadas + dublê do agente de IA
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

> Cada app possui seu próprio `tests.py`; o dashboard e os testes de segurança ficam em `core/test_dashboard.py` e `core/test_security.py`. A app `ai` divide os testes por área (`test_tools.py`, `test_services.py`, `test_views.py`, `test_commands.py`).

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

### Settings do agente de IA

Carregadas do ambiente / `.env` por `python-dotenv`, chamado no topo do `settings.py`.

| Variável | Padrão | Descrição |
|---|---|---|
| `DEEPSEEK_API_KEY` | vazio | Chave da API DeepSeek. Nunca versionada. |
| `DEEPSEEK_MODEL` | `'deepseek-chat'` | Identificador do modelo usado pelo `ChatDeepSeek` |
| `AI_ANALYSIS_ENABLED` | `True` | Feature flag; forçada a `False` quando não há chave |
| `AI_ANALYSIS_MIN_INTERVAL_MINUTES` | `15` | Intervalo mínimo entre gerações sob demanda por usuário |
| `AI_AGENT_TIMEOUT_SECONDS` | `60` | Timeout de uma execução do agente |
| `AI_AGENT_MAX_ITERATIONS` | `10` | Teto de chamadas ao modelo no loop do agente |
| `AI_ANALYSIS_MONTHS_WINDOW` | `6` | Janela padrão de meses considerada na análise |

Os helpers `env_bool()` e `env_int()` no próprio `settings.py` fazem a leitura tolerante a valores inválidos.

### INSTALLED_APPS
```
core, accounts, ai, categories, profiles, transactions, users
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
 ├── Transaction       (ForeignKey → User, Account, Category)
 └── AIAnalysis        (ForeignKey → User)
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

### AIAnalysis (`ai/models.py`)

| Campo | Tipo | Detalhes |
|---|---|---|
| `user` | `ForeignKey(User)` | `related_name='ai_analyses'`, `on_delete=CASCADE` |
| `status` | `CharField(10)` | choices: success, error |
| `summary` | `TextField` | diagnóstico geral do período |
| `insights` | `JSONField` | lista de observações |
| `tips` | `JSONField` | lista de recomendações |
| `health_score` | `PositiveSmallIntegerField` | 0 a 100, null quando falha |
| `health_label` | `CharField(20)` | choices: critical, attention, good, excellent |
| `period_start` / `period_end` | `DateField` | janela efetivamente analisada |
| `model_name` | `CharField(50)` | modelo DeepSeek usado na execução |
| `prompt_tokens` / `completion_tokens` / `total_tokens` | `PositiveIntegerField` | consumo da execução |
| `duration_ms` | `PositiveIntegerField` | duração da execução |
| `iterations` | `PositiveSmallIntegerField` | chamadas ao modelo no loop |
| `error_message` | `TextField` | texto fixo em PT-BR; nunca contém a chave da API |
| `created_at` | `DateTimeField` | `auto_now_add=True` |
| `updated_at` | `DateTimeField` | `auto_now=True` |

- `ordering = ['-created_at']`, índice em `['user', '-created_at']`
- Manager com `latest_success_for(user)` e queryset `for_user()` / `successful()`
- Properties `health_color_class` e `health_text_class` — classes Tailwind por rótulo
- O histórico é preservado: análises antigas nunca são sobrescritas, e as que falham também são gravadas

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
| `/analises/` | `AnalysisListView` | ai |
| `/analises/gerar/` | `GenerateAnalysisView` (POST) | ai |
| `/analises/<pk>/` | `AnalysisDetailView` | ai |

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
  - contexto do card de IA via `ai.services.analysis_panel_context()`, dentro de `try/except` — falha da IA não derruba a página

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

#### `ai/views.py`
- **`AnalysisListView(ListView)`** — histórico paginado de 10 em 10, filtrado por user
- **`AnalysisDetailView(DetailView)`** — queryset filtrado por user; análise de outro usuário retorna 404
- **`GenerateAnalysisView(View)`** — só aceita POST (GET retorna 405); revalida o intervalo mínimo antes de executar, chama `run_analysis_for_user()` e redireciona com `messages`. O destino vem de `next`, validado por `url_has_allowed_host_and_scheme`, com o dashboard como padrão

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
| `components/sidebar.html` | Links com ícones SVG: Dashboard, Contas, Categorias, Transações, Análises, Perfil |
| `components/messages.html` | Mensagens Django com auto-dismiss em 5s (success, error, warning, info) |
| `components/modal_confirm.html` | Modal de confirmação reutilizável para exclusões (JavaScript vanilla) |
| `components/ai_insight_card.html` | Card da última análise de IA, com estados vazio, de erro e desligado |
| `components/ai_generate_form.html` | Botão "Gerar nova análise" com spinner e bloqueio de duplo envio |

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
| `ai/analysis_list.html` | Histórico de análises com paginação (10/pág) e estado vazio |
| `ai/analysis_detail.html` | Análise completa + metadados da execução |

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
- [x] Card da última análise de IA bem-sucedida

### Análise de IA
- [x] Agente LangChain 1.0 + DeepSeek escopado a um usuário por execução
- [x] 7 tools de leitura somente-ORM, com parâmetros validados e com teto
- [x] Saída estruturada validada por schema Pydantic (`FinancialAnalysis`)
- [x] Card no dashboard com índice de saúde, resumo, insights e dicas
- [x] Histórico paginado em `/analises/` com página de detalhe
- [x] Geração sob demanda (POST) com estado de carregamento e intervalo mínimo
- [x] Geração em lote via `python manage.py run_ai_analysis`
- [x] Toda falha vira `AIAnalysis` com `status='error'`, sem quebrar o dashboard
- [x] Funcionalidade some da interface quando não há `DEEPSEEK_API_KEY`

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
- [x] Tools do agente escopadas por closure; nenhuma expõe identificador de usuário
- [x] Chave da API nunca aparece em log, mensagem de erro ou template
- [x] `{% csrf_token %}` em todos os formulários
- [x] `SECURE_BROWSER_XSS_FILTER = True`
- [x] `X_CONTENT_TYPE_OPTIONS = 'nosniff'`

### Testes
- [x] `pytest` + `pytest-django` configurados (`pytest.ini`)
- [x] Fixtures base compartilhadas em `conftest.py`
- [x] Cobertura de users, profiles, accounts, categories, transactions, dashboard, segurança e IA
- [x] Dublê do agente (`FakeAgent`) no `conftest.py` — nenhum teste chama a API real
- [x] 169 testes passando

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
| `docker-compose.yml` | Serviço `web` (build local), mapeamento `8000:8000`, volume `finanpy_db` em `/app/data`, `env_file: .env` (chave da IA), `restart: unless-stopped` |
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
docker compose exec web python manage.py run_ai_analysis
```

### Resultado da validação (T23.5)

| Verificação | Resultado |
|---|---|
| `docker compose build` | Imagem `pyfinance-web` construída |
| Subida do container | Migrações aplicadas; `System check identified no issues` |
| `GET /` e `GET /login/` | HTTP 200 |
| Arquivo do banco | `/app/data/db.sqlite3` criado, dono `appuser` |
| Persistência | Registro criado sobreviveu a `down` + `up` |
| Suíte de testes no container | 94 testes passando (tamanho da suíte à época da validação) |

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
| Sprint 8 | Agente de IA de Análise Financeira | Concluída |
| Sprint 9 | Testes | Concluída |
| Sprint 10 | Docker | Concluída |

> **Renumeração (02/08/2026):** a Sprint 8 passou a ser o Agente de IA. As antigas Sprints 8 (Testes) e 9 (Docker) viraram 9 e 10. Os identificadores de tarefa foram mantidos: `T21`–`T22` (Testes), `T23` (Docker) e `T24`–`T31` (Agente de IA).

### Progresso geral

Todo o escopo previsto está **entregue**. A conexão com a API DeepSeek foi validada em 02/08/2026 (T24.6) e a primeira análise real foi gerada com sucesso no mesmo dia, fechando a Sprint 8 sem pendências.

---

## 15. Agente de IA de Análise Financeira

Funcionalidade especificada em **RF09** e na seção **8.5** do `PRD.md`, entregue na **Sprint 8** (`T24`–`T31` do `TASKS.md`).

### Escopo

Um agente especialista em finanças pessoais analisa os dados de cada usuário (contas, categorias, transações) e produz um diagnóstico com insights e dicas práticas em português brasileiro. A última análise bem-sucedida aparece em card no dashboard; o histórico fica em `/analises/`.

### Stack

| Item | Escolha |
|---|---|
| Framework de agente | LangChain 1.0 (`langchain==1.3.14`) |
| Provedor de LLM | DeepSeek via `langchain-deepseek==1.1.0` (`ChatDeepSeek`) |
| Identificador do modelo | Setting `DEEPSEEK_MODEL` (default `deepseek-chat`) |
| Segredos | Variável de ambiente / `.env` com `python-dotenv` |
| App Django | `ai/` |

### Componentes

| Módulo | Responsabilidade |
|---|---|
| `ai/models.py` | `AIAnalysis` — grava toda análise, inclusive as que falharem |
| `ai/tools.py` | 7 tools somente-leitura, escopadas por usuário, via ORM |
| `ai/prompts.py` | System prompt do consultor financeiro (PT-BR) |
| `ai/schemas.py` | `FinancialAnalysis` (Pydantic) — saída estruturada |
| `ai/agent.py` | `build_finance_agent(user)` |
| `ai/services.py` | `run_analysis_for_user(user)` — executa, mede, persiste, trata erro |
| `ai/views.py` | Histórico, detalhe e geração sob demanda (POST) |
| `ai/management/commands/run_ai_analysis.py` | Geração em lote para todos os usuários ativos |

### Tools disponíveis ao agente

Todas somente-leitura, todas escopadas ao usuário fixado no servidor, todas devolvendo dados já agregados e serializáveis (`Decimal` convertido para `float`, datas em ISO 8601):

| Tool | Retorno |
|---|---|
| `get_financial_summary` | Saldo total, entradas/saídas do mês, balanço, nº de contas e transações |
| `get_accounts_overview` | Contas com tipo, saldo inicial e saldo atual |
| `get_expenses_by_category` | Saídas agrupadas por categoria, com valor e percentual |
| `get_income_by_category` | Entradas agrupadas por categoria |
| `get_monthly_totals` | Série mensal de entradas, saídas e balanço |
| `get_recent_transactions` | Últimas N transações |
| `get_largest_expenses` | Maiores saídas do período |

### Fluxo de execução

```
run_analysis_for_user(user)
  ├── verifica AI_ANALYSIS_ENABLED e a presença da chave
  ├── build_finance_agent(user) → ChatDeepSeek + build_tools(user) + prompt + schema
  ├── agent.invoke(...) → o modelo escolhe as tools; cada tool consulta o ORM filtrado por user
  ├── saída estruturada validada como FinancialAnalysis
  └── grava AIAnalysis (success) — ou, em qualquer falha, AIAnalysis (error)
```

### APIs do LangChain efetivamente usadas

Confirmadas via MCP context7 contra a versão instalada e registradas no docstring de `ai/agent.py`:

- `create_agent(model, tools, system_prompt=..., response_format=..., middleware=...)`
- `ToolStrategy(FinancialAnalysis)` para a saída estruturada — a DeepSeek não tem modo nativo de structured output
- `ModelCallLimitMiddleware(run_limit=...)` para o teto de iterações
- `recursion_limit` no `config` do `invoke`, como rede de segurança do grafo

### Decisões de arquitetura

- **Isolamento por usuário é a regra crítica.** O `user` é fixado no servidor por closure nas tools; a assinatura exposta ao modelo não contém identificador de usuário. Toolkits de SQL genérico são proibidos — todo acesso passa pelo ORM com `filter(user=...)`. Coberto por testes bloqueantes em `ai/test_tools.py`.
- **Execução síncrona no MVP**, com estado de carregamento na interface. Fila assíncrona fica como evolução futura, para não violar o RNF07 (simplicidade).
- **Degradação graciosa**: indisponibilidade da API, chave ausente ou feature flag desligada não quebram o dashboard. `run_analysis_for_user()` nunca propaga exceção.
- **Testes sem rede**: a suíte substitui o agente por um dublê; nenhuma chamada real à API DeepSeek.
- **Teto de iterações em duas camadas**: o `ModelCallLimitMiddleware` encerra o loop de forma limpa e o `recursion_limit` do grafo é só rede de segurança. O grafo gasta 4 super-steps por iteração — `before_model`, `model`, `after_model`, `tools` —, porque os hooks do middleware também são nós; o limite é calculado em cima disso.

### Limitação conhecida — transações com data futura

O `current_balance` da conta soma **todas** as transações, sem filtro de data (`Account.update_account_balance()`), enquanto as tools do agente agregam com `date__lte=today`. Uma transação lançada com data futura entra no saldo e fica de fora dos totais por categoria e da série mensal.

**Decidido manter assim** (02/08/2026): é o comportamento que o dashboard sempre teve, e alterá-lo exigiria mexer na agregação de saldo, que é central e coberta por testes. A inconsistência não é da IA — existiria em qualquer relatório construído sobre esses agregados.

Efeito prático: quando existe transação com data futura, o agente tende a apontar a diferença no diagnóstico (ex.: "uma despesa de R$ 110,00 ainda não refletida nas categorias de gastos"). É observação correta sobre os dados, não alucinação.

### Validação da conexão (T24.6)

Chamada mínima via `python manage.py shell` em 02/08/2026: credencial aceita, `finish_reason=stop`, 13 tokens consumidos. O identificador `deepseek-chat` é um alias — o modelo que respondeu foi `deepseek-v4-flash`. O campo `model_name` do `AIAnalysis` grava o valor configurado, não o que a API devolve.

### Execução real ponta a ponta

Primeira análise gerada contra a API real em 02/08/2026, pelo botão do dashboard:

| Métrica | Valor | Limite configurado |
|---|---|---|
| Situação | `success` | — |
| Iterações do agente | 3 | 10 (`AI_AGENT_MAX_ITERATIONS`) |
| Tokens consumidos | 9.065 | — |
| Duração | 10,5 s | 60 s (`AI_AGENT_TIMEOUT_SECONDS`) |

O fluxo completo — agente escolhendo as tools, tools consultando o ORM filtrado por usuário, saída estruturada validada pelo schema e persistência — funcionou como especificado. As margens contra os tetos de iteração e de timeout ficaram largas.

> Referência de custo: uma análise ficou em torno de 9 mil tokens. É o número a considerar ao dimensionar a geração em lote.

---

## 16. Convenções do Projeto

| Aspecto | Convenção |
|---|---|
| Linguagem do código | Inglês |
| Interface do usuário | Português Brasileiro |
| Aspas Python | Simples (`'`) |
| Views | Class-based views (CBVs) com `LoginRequiredMixin` |
| Campos de data | `DateTimeField(auto_now_add=True)` e `auto_now=True` em todos os models |
| Valores monetários | `DecimalField(max_digits=10, decimal_places=2)` |
| Segurança de dados | Toda query de listagem filtra por `user=request.user` |
| Dados expostos à IA | Tools escopadas por closure; a assinatura vista pelo modelo nunca contém `user_id` |
| Segredos | Lidos do ambiente / `.env`; nunca versionados nem escritos em log ou template |
| Saldo de conta | Recalculado via signal a cada criação/edição/exclusão de transação |
| Templates | Globais em `templates/` na raiz (não dentro das apps) |

---

## 17. Arquivos de Documentação

| Arquivo | Conteúdo |
|---|---|
| `README.md` | Descrição, stack, instalação local, execução via Docker, comandos, agente de IA, estrutura, settings configuráveis |
| `.env.example` | Chaves esperadas no `.env`, sem valores reais |
| `CLAUDE.md` | Guia de desenvolvimento para Claude Code: comandos, arquitetura, convenções, design system |
| `TASKS.md` | Lista completa de tarefas por sprint com status de conclusão |
| `PRD.md` | Product Requirements Document com requisitos do produto |
| `agents/README.md` | Índice dos agentes de IA de desenvolvimento (backend, frontend, QA, IA) |
| `agents/ai.md` | Agente especialista em LangChain 1.0 responsável pela app `ai/` |
| `relatorio.md` | Este arquivo — relatório completo do projeto |
