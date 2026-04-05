## Lista de Tarefas (Sprints)

> Legenda: `[ ]` = pendente · `[X]` = concluído

---

### Sprint 1 — Setup e Autenticação

#### [X] T1. Setup inicial do projeto

- [X] **T1.1** Criar ambiente virtual Python e ativar
  - Executar `python -m venv venv` e ativar com `source venv/bin/activate`
- [X] **T1.2** Instalar Django e gerar requirements.txt
  - `pip install django` e `pip freeze > requirements.txt`
- [X] **T1.3** Criar o projeto Django `core`
  - `django-admin startproject core .` dentro do diretório `finanpy/`
- [X] **T1.4** Criar as apps: `users`, `profiles`, `accounts`, `categories`, `transactions`
  - `python manage.py startapp <nome>` para cada app
- [X] **T1.5** Registrar todas as apps no `INSTALLED_APPS` em `core/settings.py`
  - Adicionar cada app na lista como string (ex: `'users.apps.UsersConfig'`)
- [X] **T1.6** Configurar `LANGUAGE_CODE = 'pt-br'` e `TIME_ZONE = 'America/Sao_Paulo'` em settings
  - Editar `core/settings.py`
- [X] **T1.7** Configurar `AUTH_USER_MODEL = 'users.User'` em settings
  - Adicionar a variável antes de rodar qualquer migration
- [X] **T1.8** Configurar TailwindCSS via CDN no template base
  - Adicionar `<script src="https://cdn.tailwindcss.com">` no `<head>` do `base.html`
  - Adicionar link para fonte Inter do Google Fonts
- [X] **T1.9** Criar a estrutura de diretórios `templates/` e `static/` na raiz do projeto
  - Configurar `TEMPLATES[0]['DIRS']` e `STATICFILES_DIRS` no settings
- [X] **T1.10** Criar `.gitignore` com: `venv/`, `db.sqlite3`, `__pycache__/`, `*.pyc`, `.env`
- [X] **T1.11** Executar `python manage.py migrate` para criar o banco inicial
  - Verificar que db.sqlite3 foi criado
- [X] **T1.12** Criar superusuário de desenvolvimento
  - `python manage.py createsuperuser`

#### T2. Model de Usuário Customizado

- [ ] **T2.1** Criar model `User` em `users/models.py` herdando de `AbstractUser`
  - Definir `email = EmailField(unique=True)`
  - Definir `USERNAME_FIELD = 'email'`
  - Definir `REQUIRED_FIELDS = ['first_name', 'last_name']`
  - Adicionar campos `created_at` (auto_now_add) e `updated_at` (auto_now)
- [ ] **T2.2** Criar `UserManager` customizado em `users/managers.py`
  - Herdar de `BaseUserManager`
  - Implementar `create_user()` com normalização de e-mail
  - Implementar `create_superuser()` com flags `is_staff` e `is_superuser`
- [ ] **T2.3** Registrar model User no `users/admin.py`
  - Configurar `list_display` com e-mail, nome, is_active
- [ ] **T2.4** Executar `makemigrations users` e `migrate`
  - Verificar que a migration foi criada corretamente
- [ ] **T2.5** Testar criação de usuário via Django Admin
  - Acessar `/admin/`, criar usuário com e-mail, verificar login

#### T3. Templates Base e Landing Page

- [ ] **T3.1** Criar `templates/base.html` com estrutura HTML5 completa
  - Incluir meta tags de viewport (responsividade)
  - Incluir TailwindCSS CDN e fonte Inter
  - Definir `{% block title %}`, `{% block content %}` e `{% block extra_js %}`
  - Aplicar `bg-gray-950 text-gray-100 font-sans min-h-screen`
- [ ] **T3.2** Criar `templates/base_auth.html` extendendo `base.html`
  - Layout centralizado para telas de login/cadastro (sem sidebar)
  - Card central com fundo `bg-gray-900`, borda `border-gray-700`, rounded
- [ ] **T3.3** Criar `templates/base_app.html` extendendo `base.html`
  - Incluir navbar (componente) no topo
  - Incluir sidebar (componente) na lateral esquerda
  - Área de conteúdo principal com `{% block page_content %}`
  - Incluir componente de mensagens (Django messages)
- [ ] **T3.4** Criar `templates/components/navbar.html`
  - Logo "Finanpy" com gradient `from-emerald-400 to-violet-400`
  - Nome do usuário logado à direita
  - Link de logout
  - Responsivo: menu hambúrguer em mobile
- [ ] **T3.5** Criar `templates/components/sidebar.html`
  - Links: Dashboard, Contas, Categorias, Transações, Perfil
  - Ícones SVG inline para cada item
  - Estado ativo com `text-emerald-400 bg-emerald-500/10`
  - `hidden md:block` (escondido em mobile)
- [ ] **T3.6** Criar `templates/components/messages.html`
  - Renderizar `{% for message in messages %}` com estilo por tag (success, error, warning)
  - Auto-dismiss com JavaScript simples (setTimeout + fadeOut)
- [ ] **T3.7** Criar `templates/landing.html`
  - Hero section: título com gradient, subtítulo, botões Cadastre-se e Entrar
  - Seção de funcionalidades: 3-4 cards com ícone + texto
  - Footer simples
  - Verificar se usuário está logado → redirecionar para dashboard
- [ ] **T3.8** Configurar URL da landing page em `core/urls.py`
  - Rota `''` apontando para view da landing page

#### T4. Autenticação (Cadastro, Login, Logout)

- [ ] **T4.1** Criar `users/forms.py` com formulário `UserRegistrationForm`
  - Campos: first_name, last_name, email, password1, password2
  - Herdar de `UserCreationForm` com `Meta.model = User`
  - Labels e help_texts em português
- [ ] **T4.2** Criar `users/forms.py` com formulário `EmailAuthenticationForm`
  - Herdar de `AuthenticationForm`
  - Substituir campo `username` por campo `email` (EmailField)
  - Label em português
- [ ] **T4.3** Criar view `SignUpView` em `users/views.py`
  - Usar `CreateView` com `UserRegistrationForm`
  - Após sucesso: logar o usuário com `login()` e redirecionar ao dashboard
  - Template: `templates/users/signup.html`
- [ ] **T4.4** Criar template `templates/users/signup.html`
  - Extender `base_auth.html`
  - Formulário estilizado conforme Design System (inputs, botão primário)
  - Link "Já tem conta? Faça login"
- [ ] **T4.5** Criar view de Login usando `LoginView` nativa do Django
  - Configurar `authentication_form = EmailAuthenticationForm`
  - Template: `templates/users/login.html`
  - `LOGIN_REDIRECT_URL = '/dashboard/'` no settings
- [ ] **T4.6** Criar template `templates/users/login.html`
  - Extender `base_auth.html`
  - Formulário estilizado (campo e-mail, campo senha, botão primário)
  - Link "Não tem conta? Cadastre-se"
- [ ] **T4.7** Configurar `LogoutView` nativa do Django
  - `LOGOUT_REDIRECT_URL = '/'` no settings
- [ ] **T4.8** Configurar todas as URLs de auth em `users/urls.py`
  - `signup/`, `login/`, `logout/`
- [ ] **T4.9** Incluir `users.urls` no `core/urls.py`
- [ ] **T4.10** Configurar `LOGIN_URL = '/login/'` no settings
  - Garantir que `@login_required` e `LoginRequiredMixin` redirecionem corretamente

---

### Sprint 2 — Perfil e Contas Bancárias

#### T5. Model e CRUD de Perfil

- [ ] **T5.1** Criar model `Profile` em `profiles/models.py`
  - `user = OneToOneField(User, on_delete=CASCADE, related_name='profile')`
  - `display_name = CharField(max_length=100, blank=True)`
  - Campos `created_at` e `updated_at`
  - `__str__` retornando `display_name` ou `user.email`
- [ ] **T5.2** Criar signal `post_save` em `profiles/signals.py`
  - Ao criar User, criar Profile automaticamente
  - `display_name` default = `user.first_name`
- [ ] **T5.3** Criar `profiles/apps.py` com método `ready()` importando signals
- [ ] **T5.4** Registrar Profile no admin em `profiles/admin.py`
- [ ] **T5.5** Executar `makemigrations profiles` e `migrate`
- [ ] **T5.6** Criar `profiles/forms.py` com `ProfileForm` (ModelForm)
  - Campos editáveis: `display_name` do Profile + `first_name`, `last_name`, `email` do User
  - Criar dois forms: `UserUpdateForm` e `ProfileUpdateForm`
- [ ] **T5.7** Criar view `ProfileUpdateView` em `profiles/views.py`
  - Usar `LoginRequiredMixin`
  - Renderizar ambos os formulários no mesmo template
  - Salvar ambos no `form_valid`
  - Template: `templates/profiles/profile_edit.html`
- [ ] **T5.8** Criar template `templates/profiles/profile_edit.html`
  - Extender `base_app.html`
  - Formulário estilizado conforme Design System
  - Título "Meu Perfil"
- [ ] **T5.9** Configurar URLs em `profiles/urls.py` e incluir em `core/urls.py`
  - Rota: `perfil/`

#### T6. Model de Conta Bancária

- [ ] **T6.1** Criar model `Account` em `accounts/models.py`
  - `user = ForeignKey(User, on_delete=CASCADE, related_name='accounts')`
  - `name = CharField(max_length=100)`
  - `account_type = CharField(choices=ACCOUNT_TYPE_CHOICES)`
    - Choices: `('checking', 'Conta Corrente')`, `('savings', 'Poupança')`, `('wallet', 'Carteira')`, `('investment', 'Investimento')`
  - `initial_balance = DecimalField(max_digits=10, decimal_places=2, default=0)`
  - `current_balance = DecimalField(max_digits=10, decimal_places=2, default=0)`
  - Campos `created_at` e `updated_at`
  - Método `__str__` retornando nome da conta
- [ ] **T6.2** Sobrescrever `save()` para que na criação `current_balance = initial_balance`
- [ ] **T6.3** Registrar model no admin com `list_display`, `list_filter`
- [ ] **T6.4** Executar `makemigrations accounts` e `migrate`
- [ ] **T6.5** Testar criação de conta via admin

#### T7. CRUD de Contas Bancárias (Views e Templates)

- [ ] **T7.1** Criar `accounts/forms.py` com `AccountForm` (ModelForm)
  - Campos: name, account_type, initial_balance
  - Labels em português
  - Widget de initial_balance com step="0.01"
- [ ] **T7.2** Criar `AccountListView` em `accounts/views.py`
  - `LoginRequiredMixin` + `ListView`
  - Filtrar `queryset` pelo `request.user`
  - Template: `templates/accounts/account_list.html`
- [ ] **T7.3** Criar template `templates/accounts/account_list.html`
  - Extender `base_app.html`
  - Título "Minhas Contas"
  - Botão "Nova Conta" (link para create)
  - Tabela responsiva com: nome, tipo, saldo atual, ações (editar/excluir)
  - Valores positivos em verde, negativos em vermelho
  - Estado vazio: mensagem amigável "Nenhuma conta cadastrada"
- [ ] **T7.4** Criar `AccountCreateView` em `accounts/views.py`
  - `LoginRequiredMixin` + `CreateView`
  - No `form_valid`, atribuir `user = request.user`
  - Mensagem de sucesso
  - Redirecionar para lista
  - Template: `templates/accounts/account_form.html`
- [ ] **T7.5** Criar template `templates/accounts/account_form.html`
  - Extender `base_app.html`
  - Formulário estilizado conforme Design System
  - Reutilizado para create e update (título dinâmico)
- [ ] **T7.6** Criar `AccountUpdateView` em `accounts/views.py`
  - `LoginRequiredMixin` + `UpdateView`
  - Filtrar queryset pelo user para segurança
  - Campos editáveis: name, account_type (não initial_balance)
  - Mensagem de sucesso
  - Template reutilizado: `account_form.html`
- [ ] **T7.7** Criar `AccountDeleteView` em `accounts/views.py`
  - `LoginRequiredMixin` + `DeleteView`
  - Filtrar queryset pelo user
  - Template de confirmação: `templates/accounts/account_confirm_delete.html`
  - Mensagem de sucesso
- [ ] **T7.8** Criar template `templates/accounts/account_confirm_delete.html`
  - Modal/card de confirmação conforme Design System
  - Botões Cancelar e Excluir
- [ ] **T7.9** Configurar URLs em `accounts/urls.py`
  - `contas/` → lista
  - `contas/nova/` → criar
  - `contas/<pk>/editar/` → editar
  - `contas/<pk>/excluir/` → excluir
- [ ] **T7.10** Incluir `accounts.urls` em `core/urls.py`

---

### Sprint 3 — Categorias e Categorias Padrão

#### T8. Model de Categoria

- [ ] **T8.1** Criar model `Category` em `categories/models.py`
  - `user = ForeignKey(User, on_delete=CASCADE, related_name='categories')`
  - `name = CharField(max_length=50)`
  - `transaction_type = CharField(choices=TRANSACTION_TYPE_CHOICES)`
    - Choices: `('income', 'Entrada')`, `('expense', 'Saída')`
  - Campos `created_at` e `updated_at`
  - `class Meta: ordering = ['name']` e `unique_together = ['user', 'name', 'transaction_type']`
  - `__str__` retornando nome
- [ ] **T8.2** Registrar no admin
- [ ] **T8.3** Executar `makemigrations categories` e `migrate`

#### T9. Categorias Padrão via Signal

- [ ] **T9.1** Criar `categories/signals.py`
  - Signal `post_save` no model `User`
  - Ao criar novo usuário (`created=True`), criar categorias padrão:
    - Entrada: Salário, Freelance, Investimentos, Outros
    - Saída: Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros
- [ ] **T9.2** Configurar `categories/apps.py` com `ready()` importando signals
- [ ] **T9.3** Testar: criar novo usuário e verificar se categorias foram criadas

#### T10. CRUD de Categorias (Views e Templates)

- [ ] **T10.1** Criar `categories/forms.py` com `CategoryForm` (ModelForm)
  - Campos: name, transaction_type
  - Labels em português
- [ ] **T10.2** Criar `CategoryListView` em `categories/views.py`
  - `LoginRequiredMixin` + `ListView`
  - Filtrar pelo user
  - Template: `templates/categories/category_list.html`
- [ ] **T10.3** Criar template `templates/categories/category_list.html`
  - Extender `base_app.html`
  - Título "Minhas Categorias"
  - Botão "Nova Categoria"
  - Tabela com: nome, tipo (badge verde/vermelho), ações
  - Estado vazio com mensagem amigável
- [ ] **T10.4** Criar `CategoryCreateView`
  - `LoginRequiredMixin` + `CreateView`
  - Atribuir user no `form_valid`
  - Mensagem de sucesso
  - Template: `templates/categories/category_form.html`
- [ ] **T10.5** Criar template `templates/categories/category_form.html`
  - Formulário estilizado, reutilizado para create/update
- [ ] **T10.6** Criar `CategoryUpdateView`
  - Filtrar queryset pelo user
  - Mensagem de sucesso
- [ ] **T10.7** Criar `CategoryDeleteView`
  - Filtrar queryset pelo user
  - Impedir exclusão se houver transações vinculadas (verificar no `delete()` ou `form_valid()`)
  - Template: `templates/categories/category_confirm_delete.html`
- [ ] **T10.8** Criar template de confirmação de exclusão
- [ ] **T10.9** Configurar URLs em `categories/urls.py`
  - `categorias/`, `categorias/nova/`, `categorias/<pk>/editar/`, `categorias/<pk>/excluir/`
- [ ] **T10.10** Incluir `categories.urls` em `core/urls.py`

---

### Sprint 4 — Transações

#### T11. Model de Transação

- [ ] **T11.1** Criar model `Transaction` em `transactions/models.py`
  - `user = ForeignKey(User, on_delete=CASCADE, related_name='transactions')`
  - `account = ForeignKey(Account, on_delete=CASCADE, related_name='transactions')`
  - `category = ForeignKey(Category, on_delete=PROTECT, related_name='transactions')`
  - `description = CharField(max_length=200)`
  - `amount = DecimalField(max_digits=10, decimal_places=2)`
  - `transaction_type = CharField(choices: income/expense)`
  - `date = DateField()`
  - Campos `created_at` e `updated_at`
  - `class Meta: ordering = ['-date', '-created_at']`
  - `__str__` retornando `f'{description} - R$ {amount}'`
- [ ] **T11.2** Registrar no admin com `list_display`, `list_filter`, `search_fields`
- [ ] **T11.3** Executar `makemigrations transactions` e `migrate`

#### T12. Lógica de Atualização de Saldo

- [ ] **T12.1** Criar método `update_account_balance()` no model `Account`
  - Recalcula `current_balance` = `initial_balance` + soma de entradas - soma de saídas
  - Usar `aggregate` do Django ORM
- [ ] **T12.2** Criar `transactions/signals.py` com signals `post_save` e `post_delete`
  - Após salvar ou excluir transação, chamar `transaction.account.update_account_balance()`
- [ ] **T12.3** Configurar `transactions/apps.py` com `ready()` importando signals
- [ ] **T12.4** Testar: criar transações e verificar que saldo da conta atualiza corretamente

#### T13. CRUD de Transações (Views e Templates)

- [ ] **T13.1** Criar `transactions/forms.py` com `TransactionForm` (ModelForm)
  - Campos: description, amount, date, transaction_type, account, category
  - Labels em português
  - Filtrar `account` e `category` pelo user no `__init__`
  - Widget de date com `type="date"`
  - Widget de amount com `step="0.01"`
- [ ] **T13.2** Criar `TransactionListView` em `transactions/views.py`
  - `LoginRequiredMixin` + `ListView`
  - Filtrar pelo user
  - Paginação: 20 por página
  - Template: `templates/transactions/transaction_list.html`
- [ ] **T13.3** Implementar filtros na `TransactionListView`
  - Receber via GET: `date_from`, `date_to`, `transaction_type`, `account`, `category`
  - Aplicar filtros no `get_queryset()`
  - Passar filtros ativos ao contexto para manter estado no template
- [ ] **T13.4** Criar template `templates/transactions/transaction_list.html`
  - Extender `base_app.html`
  - Título "Minhas Transações"
  - Barra de filtros no topo (inputs de data, selects de tipo/conta/categoria, botão filtrar)
  - Botão "Nova Transação"
  - Tabela responsiva: data, descrição, categoria, conta, valor (verde/vermelho), ações
  - Paginação estilizada no rodapé
  - Estado vazio
- [ ] **T13.5** Criar `TransactionCreateView`
  - `LoginRequiredMixin` + `CreateView`
  - Atribuir user no `form_valid`
  - Filtrar account/category pelo user via `get_form()`
  - Mensagem de sucesso
  - Template: `templates/transactions/transaction_form.html`
- [ ] **T13.6** Criar template `templates/transactions/transaction_form.html`
  - Formulário estilizado, reutilizado para create/update
- [ ] **T13.7** Criar `TransactionUpdateView`
  - Filtrar queryset pelo user
  - Mensagem de sucesso
- [ ] **T13.8** Criar `TransactionDeleteView`
  - Filtrar queryset pelo user
  - Template: `templates/transactions/transaction_confirm_delete.html`
  - Mensagem de sucesso
- [ ] **T13.9** Criar template de confirmação de exclusão
- [ ] **T13.10** Configurar URLs em `transactions/urls.py`
  - `transacoes/`, `transacoes/nova/`, `transacoes/<pk>/editar/`, `transacoes/<pk>/excluir/`
- [ ] **T13.11** Incluir `transactions.urls` em `core/urls.py`

---

### Sprint 5 — Dashboard

#### T14. View e Template do Dashboard

- [ ] **T14.1** Criar view `DashboardView` (pode ficar em `core/views.py` ou app separada)
  - `LoginRequiredMixin` + `TemplateView`
  - No `get_context_data`, calcular:
    - `total_balance`: soma de `current_balance` de todas as contas do user
    - `monthly_income`: soma de transações tipo income do mês corrente
    - `monthly_expense`: soma de transações tipo expense do mês corrente
    - `monthly_balance`: income - expense
    - `recent_transactions`: últimas 5 transações do user
    - `expenses_by_category`: transações de saída do mês agrupadas por categoria com soma
- [ ] **T14.2** Criar template `templates/dashboard.html`
  - Extender `base_app.html`
  - Grid com 4 cards de resumo:
    - Saldo Total (com ícone, valor grande, gradient top border emerald)
    - Entradas do Mês (texto verde)
    - Saídas do Mês (texto vermelho)
    - Balanço do Mês (verde se positivo, vermelho se negativo)
  - Seção "Últimas Transações": mini-tabela com 5 últimas
  - Seção "Gastos por Categoria": lista de categorias com barra de progresso ou valor
- [ ] **T14.3** Configurar URL do dashboard em `core/urls.py`
  - Rota: `dashboard/`
- [ ] **T14.4** Verificar que `LOGIN_REDIRECT_URL = '/dashboard/'` está no settings
- [ ] **T14.5** Garantir que o link "Dashboard" na sidebar esteja ativo quando na rota correta

---

### Sprint 6 — Refinamentos e Responsividade

#### T15. Menu Mobile

- [ ] **T15.1** Implementar toggle de sidebar mobile com JavaScript vanilla
  - Botão hamburger na navbar (visível apenas em mobile)
  - Sidebar abre como overlay com fundo escuro (`bg-black/60`)
  - Botão de fechar (X) dentro da sidebar mobile
- [ ] **T15.2** Garantir que ao clicar em um link da sidebar mobile, ela fecha
- [ ] **T15.3** Testar responsividade em todas as telas (320px a 1440px)

#### T16. Modal de Confirmação de Exclusão (JavaScript)

- [ ] **T16.1** Criar componente `templates/components/modal_confirm.html`
  - Modal genérico reutilizável via `{% include %}` com variáveis de contexto
  - JavaScript vanilla para abrir/fechar modal
- [ ] **T16.2** Integrar modal nas views de exclusão (contas, categorias, transações)
  - Substituir página de confirmação por modal inline na lista
- [ ] **T16.3** Testar fluxo de exclusão com modal em todas as entidades

#### T17. Refinamentos Visuais

- [ ] **T17.1** Adicionar ícones SVG inline na sidebar (Dashboard, Contas, Categorias, etc.)
- [ ] **T17.2** Formatar valores monetários como `R$ 1.234,56` nos templates
  - Criar template filter customizado `currency_brl` ou usar `floatformat` + formatação
- [ ] **T17.3** Adicionar badges de tipo nas categorias (verde "Entrada", vermelho "Saída")
- [ ] **T17.4** Estilizar paginação da listagem de transações
  - Botões Previous/Next com estilo do Design System
- [ ] **T17.5** Adicionar animação de fade nas mensagens de feedback (auto-dismiss em 5s)
- [ ] **T17.6** Revisar consistência visual de todas as telas com o Design System
  - Verificar espaçamentos, cores, bordas, fontes
- [ ] **T17.7** Adicionar estados de hover e focus em todos os elementos interativos
- [ ] **T17.8** Garantir que a landing page não é acessível por usuários logados (redirect)

---

### Sprint 7 — Polimento e Preparação para Produção

#### T18. Validações e Segurança

- [ ] **T18.1** Garantir que todas as views autenticadas usam `LoginRequiredMixin`
- [ ] **T18.2** Garantir que todas as queries filtram por `user=request.user`
  - Testar acesso direto a URLs de outro usuário (deve retornar 404)
- [ ] **T18.3** Validar que valor de transação é sempre positivo no form
- [ ] **T18.4** Validar que transação só aceita categorias do mesmo tipo (income/expense)
- [ ] **T18.5** Adicionar `{% csrf_token %}` em todos os formulários (verificar)
- [ ] **T18.6** Configurar `SECURE_BROWSER_XSS_FILTER = True` e `X_CONTENT_TYPE_OPTIONS` no settings

#### T19. Template Filters e Helpers

- [ ] **T19.1** Criar `templatetags/` em uma app (ex: `core` ou app dedicada)
  - Criar `format_filters.py` com filtro `brl_currency` para formatar Decimal → `R$ X.XXX,XX`
- [ ] **T19.2** Criar filtro `active_link` para sidebar (marca item ativo por URL)
- [ ] **T19.3** Registrar templatetags e usar em todos os templates relevantes

#### T20. README e Documentação

- [ ] **T20.1** Criar `README.md` com:
  - Descrição do projeto
  - Stack tecnológica
  - Instruções de instalação e setup local
  - Comandos úteis (runserver, migrate, createsuperuser)
  - Estrutura de diretórios
- [ ] **T20.2** Documentar variáveis de settings que podem ser customizadas

---

### Sprint 8 — Testes (Sprint Final)

#### T21. Setup de Testes

- [ ] **T21.1** Configurar `pytest` e `pytest-django` no projeto
  - Adicionar ao `requirements.txt`
  - Criar `pytest.ini` ou `pyproject.toml` com configuração Django
- [ ] **T21.2** Criar fixtures base: usuário de teste, conta, categoria, transação

#### T22. Testes por App

- [ ] **T22.1** Testes `users`: cadastro, login, login com e-mail inválido, logout
- [ ] **T22.2** Testes `profiles`: edição de perfil, criação automática via signal
- [ ] **T22.3** Testes `accounts`: CRUD completo, saldo inicial = saldo atual na criação
- [ ] **T22.4** Testes `categories`: CRUD, categorias padrão via signal, proteção de exclusão
- [ ] **T22.5** Testes `transactions`: CRUD, atualização de saldo, filtros
- [ ] **T22.6** Testes `dashboard`: cálculos corretos de saldos e totais mensais
- [ ] **T22.7** Testes de segurança: acesso a dados de outro usuário retorna 404

---

### Sprint 9 — Docker (Sprint Final)

#### T23. Dockerização

- [ ] **T23.1** Criar `Dockerfile` com Python 3.12 + pip install de requirements
- [ ] **T23.2** Criar `docker-compose.yml` com serviço web
- [ ] **T23.3** Configurar volume para persistir db.sqlite3
- [ ] **T23.4** Documentar no README os comandos Docker
- [ ] **T23.5** Testar build e execução completa via Docker
