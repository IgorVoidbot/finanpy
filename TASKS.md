## Lista de Tarefas (Sprints)

> Legenda: `[ ]` = pendente · `[X]` = concluído
>
> **Nota de numeração (02/08/2026):** a Sprint 8 passou a ser o Agente de IA. As antigas Sprints 8 (Testes) e 9 (Docker), já concluídas, foram renumeradas para **9** e **10**. Os identificadores de tarefa (`T21`–`T23`) foram mantidos como estavam para não invalidar as referências do histórico de commits e da documentação — por isso a Sprint 8 usa `T24`–`T31`.

---

### [X] Sprint 1 — Setup e Autenticação

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

#### [X] T2. Model de Usuário Customizado

- [X] **T2.1** Criar model `User` em `users/models.py` herdando de `AbstractUser`
  - Definir `email = EmailField(unique=True)`
  - Definir `USERNAME_FIELD = 'email'`
  - Definir `REQUIRED_FIELDS = ['first_name', 'last_name']`
  - Adicionar campos `created_at` (auto_now_add) e `updated_at` (auto_now)
- [X] **T2.2** Criar `UserManager` customizado em `users/managers.py`
  - Herdar de `BaseUserManager`
  - Implementar `create_user()` com normalização de e-mail
  - Implementar `create_superuser()` com flags `is_staff` e `is_superuser`
- [X] **T2.3** Registrar model User no `users/admin.py`
  - Configurar `list_display` com e-mail, nome, is_active
- [X] **T2.4** Executar `makemigrations users` e `migrate`
  - Verificar que a migration foi criada corretamente
- [X] **T2.5** Testar criação de usuário via Django Admin
  - Acessar `/admin/`, criar usuário com e-mail, verificar login

#### [X] T3. Templates Base e Landing Page

- [X] **T3.1** Criar `templates/base.html` com estrutura HTML5 completa
  - Incluir meta tags de viewport (responsividade)
  - Incluir TailwindCSS CDN e fonte Inter
  - Definir `{% block title %}`, `{% block content %}` e `{% block extra_js %}`
  - Aplicar `bg-gray-950 text-gray-100 font-sans min-h-screen`
- [X] **T3.2** Criar `templates/base_auth.html` extendendo `base.html`
  - Layout centralizado para telas de login/cadastro (sem sidebar)
  - Card central com fundo `bg-gray-900`, borda `border-gray-700`, rounded
- [X] **T3.3** Criar `templates/base_app.html` extendendo `base.html`
  - Incluir navbar (componente) no topo
  - Incluir sidebar (componente) na lateral esquerda
  - Área de conteúdo principal com `{% block page_content %}`
  - Incluir componente de mensagens (Django messages)
- [X] **T3.4** Criar `templates/components/navbar.html`
  - Logo "Finanpy" com gradient `from-emerald-400 to-violet-400`
  - Nome do usuário logado à direita
  - Link de logout
  - Responsivo: menu hambúrguer em mobile
- [X] **T3.5** Criar `templates/components/sidebar.html`
  - Links: Dashboard, Contas, Categorias, Transações, Perfil
  - Ícones SVG inline para cada item
  - Estado ativo com `text-emerald-400 bg-emerald-500/10`
  - `hidden md:block` (escondido em mobile)
- [X] **T3.6** Criar `templates/components/messages.html`
  - Renderizar `{% for message in messages %}` com estilo por tag (success, error, warning)
  - Auto-dismiss com JavaScript simples (setTimeout + fadeOut)
- [X] **T3.7** Criar `templates/landing.html`
  - Hero section: título com gradient, subtítulo, botões Cadastre-se e Entrar
  - Seção de funcionalidades: 3-4 cards com ícone + texto
  - Footer simples
  - Verificar se usuário está logado → redirecionar para dashboard
- [X] **T3.8** Configurar URL da landing page em `core/urls.py`
  - Rota `''` apontando para view da landing page

#### [X] T4. Autenticação (Cadastro, Login, Logout)

- [X] **T4.1** Criar `users/forms.py` com formulário `UserRegistrationForm`
  - Campos: first_name, last_name, email, password1, password2
  - Herdar de `UserCreationForm` com `Meta.model = User`
  - Labels e help_texts em português
- [X] **T4.2** Criar `users/forms.py` com formulário `EmailAuthenticationForm`
  - Herdar de `AuthenticationForm`
  - Substituir campo `username` por campo `email` (EmailField)
  - Label em português
- [X] **T4.3** Criar view `SignUpView` em `users/views.py`
  - Usar `CreateView` com `UserRegistrationForm`
  - Após sucesso: logar o usuário com `login()` e redirecionar ao dashboard
  - Template: `templates/users/signup.html`
- [X] **T4.4** Criar template `templates/users/signup.html`
  - Extender `base_auth.html`
  - Formulário estilizado conforme Design System (inputs, botão primário)
  - Link "Já tem conta? Faça login"
- [X] **T4.5** Criar view de Login usando `LoginView` nativa do Django
  - Configurar `authentication_form = EmailAuthenticationForm`
  - Template: `templates/users/login.html`
  - `LOGIN_REDIRECT_URL = '/dashboard/'` no settings
- [X] **T4.6** Criar template `templates/users/login.html`
  - Extender `base_auth.html`
  - Formulário estilizado (campo e-mail, campo senha, botão primário)
  - Link "Não tem conta? Cadastre-se"
- [X] **T4.7** Configurar `LogoutView` nativa do Django
  - `LOGOUT_REDIRECT_URL = '/'` no settings
- [X] **T4.8** Configurar todas as URLs de auth em `users/urls.py`
  - `signup/`, `login/`, `logout/`
- [X] **T4.9** Incluir `users.urls` no `core/urls.py`
- [X] **T4.10** Configurar `LOGIN_URL = '/login/'` no settings
  - Garantir que `@login_required` e `LoginRequiredMixin` redirecionem corretamente

---

### Sprint 2 — Perfil e Contas Bancárias

#### [X] T5. Model e CRUD de Perfil

- [X] **T5.1** Criar model `Profile` em `profiles/models.py`
  - `user = OneToOneField(User, on_delete=CASCADE, related_name='profile')`
  - `display_name = CharField(max_length=100, blank=True)`
  - Campos `created_at` e `updated_at`
  - `__str__` retornando `display_name` ou `user.email`
- [X] **T5.2** Criar signal `post_save` em `profiles/signals.py`
  - Ao criar User, criar Profile automaticamente
  - `display_name` default = `user.first_name`
- [X] **T5.3** Criar `profiles/apps.py` com método `ready()` importando signals
- [X] **T5.4** Registrar Profile no admin em `profiles/admin.py`
- [X] **T5.5** Executar `makemigrations profiles` e `migrate`
- [X] **T5.6** Criar `profiles/forms.py` com `ProfileForm` (ModelForm)
  - Campos editáveis: `display_name` do Profile + `first_name`, `last_name`, `email` do User
  - Criar dois forms: `UserUpdateForm` e `ProfileUpdateForm`
- [X] **T5.7** Criar view `ProfileUpdateView` em `profiles/views.py`
  - Usar `LoginRequiredMixin`
  - Renderizar ambos os formulários no mesmo template
  - Salvar ambos no `form_valid`
  - Template: `templates/profiles/profile_edit.html`
- [X] **T5.8** Criar template `templates/profiles/profile_edit.html`
  - Extender `base_app.html`
  - Formulário estilizado conforme Design System
  - Título "Meu Perfil"
- [X] **T5.9** Configurar URLs em `profiles/urls.py` e incluir em `core/urls.py`
  - Rota: `perfil/`

#### [X] T6. Model de Conta Bancária

- [X] **T6.1** Criar model `Account` em `accounts/models.py`
  - `user = ForeignKey(User, on_delete=CASCADE, related_name='accounts')`
  - `name = CharField(max_length=100)`
  - `account_type = CharField(choices=ACCOUNT_TYPE_CHOICES)`
    - Choices: `('checking', 'Conta Corrente')`, `('savings', 'Poupança')`, `('wallet', 'Carteira')`, `('investment', 'Investimento')`
  - `initial_balance = DecimalField(max_digits=10, decimal_places=2, default=0)`
  - `current_balance = DecimalField(max_digits=10, decimal_places=2, default=0)`
  - Campos `created_at` e `updated_at`
  - Método `__str__` retornando nome da conta
- [X] **T6.2** Sobrescrever `save()` para que na criação `current_balance = initial_balance`
- [X] **T6.3** Registrar model no admin com `list_display`, `list_filter`
- [X] **T6.4** Executar `makemigrations accounts` e `migrate`
- [X] **T6.5** Testar criação de conta via admin

#### [X] T7. CRUD de Contas Bancárias (Views e Templates)

- [X] **T7.1** Criar `accounts/forms.py` com `AccountForm` (ModelForm)
  - Campos: name, account_type, initial_balance
  - Labels em português
  - Widget de initial_balance com step="0.01"
- [X] **T7.2** Criar `AccountListView` em `accounts/views.py`
  - `LoginRequiredMixin` + `ListView`
  - Filtrar `queryset` pelo `request.user`
  - Template: `templates/accounts/account_list.html`
- [X] **T7.3** Criar template `templates/accounts/account_list.html`
  - Extender `base_app.html`
  - Título "Minhas Contas"
  - Botão "Nova Conta" (link para create)
  - Tabela responsiva com: nome, tipo, saldo atual, ações (editar/excluir)
  - Valores positivos em verde, negativos em vermelho
  - Estado vazio: mensagem amigável "Nenhuma conta cadastrada"
- [X] **T7.4** Criar `AccountCreateView` em `accounts/views.py`
  - `LoginRequiredMixin` + `CreateView`
  - No `form_valid`, atribuir `user = request.user`
  - Mensagem de sucesso
  - Redirecionar para lista
  - Template: `templates/accounts/account_form.html`
- [X] **T7.5** Criar template `templates/accounts/account_form.html`
  - Extender `base_app.html`
  - Formulário estilizado conforme Design System
  - Reutilizado para create e update (título dinâmico)
- [X] **T7.6** Criar `AccountUpdateView` em `accounts/views.py`
  - `LoginRequiredMixin` + `UpdateView`
  - Filtrar queryset pelo user para segurança
  - Campos editáveis: name, account_type (não initial_balance)
  - Mensagem de sucesso
  - Template reutilizado: `account_form.html`
- [X] **T7.7** Criar `AccountDeleteView` em `accounts/views.py`
  - `LoginRequiredMixin` + `DeleteView`
  - Filtrar queryset pelo user
  - Template de confirmação: `templates/accounts/account_confirm_delete.html`
  - Mensagem de sucesso
- [X] **T7.8** Criar template `templates/accounts/account_confirm_delete.html`
  - Modal/card de confirmação conforme Design System
  - Botões Cancelar e Excluir
- [X] **T7.9** Configurar URLs em `accounts/urls.py`
  - `contas/` → lista
  - `contas/nova/` → criar
  - `contas/<pk>/editar/` → editar
  - `contas/<pk>/excluir/` → excluir
- [X] **T7.10** Incluir `accounts.urls` em `core/urls.py`

---

### [X] Sprint 3 — Categorias e Categorias Padrão

#### [X] T8. Model de Categoria

- [X] **T8.1** Criar model `Category` em `categories/models.py`
  - `user = ForeignKey(User, on_delete=CASCADE, related_name='categories')`
  - `name = CharField(max_length=50)`
  - `transaction_type = CharField(choices=TRANSACTION_TYPE_CHOICES)`
    - Choices: `('income', 'Entrada')`, `('expense', 'Saída')`
  - Campos `created_at` e `updated_at`
  - `class Meta: ordering = ['name']` e `unique_together = ['user', 'name', 'transaction_type']`
  - `__str__` retornando nome
- [X] **T8.2** Registrar no admin
- [X] **T8.3** Executar `makemigrations categories` e `migrate`

#### [X] T9. Categorias Padrão via Signal

- [X] **T9.1** Criar `categories/signals.py`
  - Signal `post_save` no model `User`
  - Ao criar novo usuário (`created=True`), criar categorias padrão:
    - Entrada: Salário, Freelance, Investimentos, Outros
    - Saída: Alimentação, Transporte, Moradia, Lazer, Saúde, Educação, Outros
- [X] **T9.2** Configurar `categories/apps.py` com `ready()` importando signals
- [X] **T9.3** Testar: criar novo usuário e verificar se categorias foram criadas

#### [X] T10. CRUD de Categorias (Views e Templates)

- [X] **T10.1** Criar `categories/forms.py` com `CategoryForm` (ModelForm)
  - Campos: name, transaction_type
  - Labels em português
- [X] **T10.2** Criar `CategoryListView` em `categories/views.py`
  - `LoginRequiredMixin` + `ListView`
  - Filtrar pelo user
  - Template: `templates/categories/category_list.html`
- [X] **T10.3** Criar template `templates/categories/category_list.html`
  - Extender `base_app.html`
  - Título "Minhas Categorias"
  - Botão "Nova Categoria"
  - Tabela com: nome, tipo (badge verde/vermelho), ações
  - Estado vazio com mensagem amigável
- [X] **T10.4** Criar `CategoryCreateView`
  - `LoginRequiredMixin` + `CreateView`
  - Atribuir user no `form_valid`
  - Mensagem de sucesso
  - Template: `templates/categories/category_form.html`
- [X] **T10.5** Criar template `templates/categories/category_form.html`
  - Formulário estilizado, reutilizado para create/update
- [X] **T10.6** Criar `CategoryUpdateView`
  - Filtrar queryset pelo user
  - Mensagem de sucesso
- [X] **T10.7** Criar `CategoryDeleteView`
  - Filtrar queryset pelo user
  - Impedir exclusão se houver transações vinculadas (verificar no `delete()` ou `form_valid()`)
  - Template: `templates/categories/category_confirm_delete.html`
- [X] **T10.8** Criar template de confirmação de exclusão
- [X] **T10.9** Configurar URLs em `categories/urls.py`
  - `categorias/`, `categorias/nova/`, `categorias/<pk>/editar/`, `categorias/<pk>/excluir/`
- [X] **T10.10** Incluir `categories.urls` em `core/urls.py`

---

### [X] Sprint 4 — Transações

#### [X] T11. Model de Transação

- [X] **T11.1** Criar model `Transaction` em `transactions/models.py`
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
- [X] **T11.2** Registrar no admin com `list_display`, `list_filter`, `search_fields`
- [X] **T11.3** Executar `makemigrations transactions` e `migrate`

#### [X] T12. Lógica de Atualização de Saldo

- [X] **T12.1** Criar método `update_account_balance()` no model `Account`
  - Recalcula `current_balance` = `initial_balance` + soma de entradas - soma de saídas
  - Usar `aggregate` do Django ORM
- [X] **T12.2** Criar `transactions/signals.py` com signals `post_save` e `post_delete`
  - Após salvar ou excluir transação, chamar `transaction.account.update_account_balance()`
- [X] **T12.3** Configurar `transactions/apps.py` com `ready()` importando signals
- [X] **T12.4** Testar: criar transações e verificar que saldo da conta atualiza corretamente

#### [X] T13. CRUD de Transações (Views e Templates)

- [X] **T13.1** Criar `transactions/forms.py` com `TransactionForm` (ModelForm)
  - Campos: description, amount, date, transaction_type, account, category
  - Labels em português
  - Filtrar `account` e `category` pelo user no `__init__`
  - Widget de date com `type="date"`
  - Widget de amount com `step="0.01"`
- [X] **T13.2** Criar `TransactionListView` em `transactions/views.py`
  - `LoginRequiredMixin` + `ListView`
  - Filtrar pelo user
  - Paginação: 20 por página
  - Template: `templates/transactions/transaction_list.html`
- [X] **T13.3** Implementar filtros na `TransactionListView`
  - Receber via GET: `date_from`, `date_to`, `transaction_type`, `account`, `category`
  - Aplicar filtros no `get_queryset()`
  - Passar filtros ativos ao contexto para manter estado no template
- [X] **T13.4** Criar template `templates/transactions/transaction_list.html`
  - Extender `base_app.html`
  - Título "Minhas Transações"
  - Barra de filtros no topo (inputs de data, selects de tipo/conta/categoria, botão filtrar)
  - Botão "Nova Transação"
  - Tabela responsiva: data, descrição, categoria, conta, valor (verde/vermelho), ações
  - Paginação estilizada no rodapé
  - Estado vazio
- [X] **T13.5** Criar `TransactionCreateView`
  - `LoginRequiredMixin` + `CreateView`
  - Atribuir user no `form_valid`
  - Filtrar account/category pelo user via `get_form()`
  - Mensagem de sucesso
  - Template: `templates/transactions/transaction_form.html`
- [X] **T13.6** Criar template `templates/transactions/transaction_form.html`
  - Formulário estilizado, reutilizado para create/update
- [X] **T13.7** Criar `TransactionUpdateView`
  - Filtrar queryset pelo user
  - Mensagem de sucesso
- [X] **T13.8** Criar `TransactionDeleteView`
  - Filtrar queryset pelo user
  - Template: `templates/transactions/transaction_confirm_delete.html`
  - Mensagem de sucesso
- [X] **T13.9** Criar template de confirmação de exclusão
- [X] **T13.10** Configurar URLs em `transactions/urls.py`
  - `transacoes/`, `transacoes/nova/`, `transacoes/<pk>/editar/`, `transacoes/<pk>/excluir/`
- [X] **T13.11** Incluir `transactions.urls` em `core/urls.py`

---

### [X] Sprint 5 — Dashboard

#### [X] T14. View e Template do Dashboard

- [X] **T14.1** Criar view `DashboardView` (pode ficar em `core/views.py` ou app separada)
  - `LoginRequiredMixin` + `TemplateView`
  - No `get_context_data`, calcular:
    - `total_balance`: soma de `current_balance` de todas as contas do user
    - `monthly_income`: soma de transações tipo income do mês corrente
    - `monthly_expense`: soma de transações tipo expense do mês corrente
    - `monthly_balance`: income - expense
    - `recent_transactions`: últimas 5 transações do user
    - `expenses_by_category`: transações de saída do mês agrupadas por categoria com soma
- [X] **T14.2** Criar template `templates/dashboard.html`
  - Extender `base_app.html`
  - Grid com 4 cards de resumo:
    - Saldo Total (com ícone, valor grande, gradient top border emerald)
    - Entradas do Mês (texto verde)
    - Saídas do Mês (texto vermelho)
    - Balanço do Mês (verde se positivo, vermelho se negativo)
  - Seção "Últimas Transações": mini-tabela com 5 últimas
  - Seção "Gastos por Categoria": lista de categorias com barra de progresso ou valor
- [X] **T14.3** Configurar URL do dashboard em `core/urls.py`
  - Rota: `dashboard/`
- [X] **T14.4** Verificar que `LOGIN_REDIRECT_URL = '/dashboard/'` está no settings
- [X] **T14.5** Garantir que o link "Dashboard" na sidebar esteja ativo quando na rota correta

---

### [X] Sprint 6 — Refinamentos e Responsividade

#### [X] T15. Menu Mobile

- [X] **T15.1** Implementar toggle de sidebar mobile com JavaScript vanilla
  - Botão hamburger na navbar (visível apenas em mobile)
  - Sidebar abre como overlay com fundo escuro (`bg-black/60`)
  - Botão de fechar (X) dentro da sidebar mobile
- [X] **T15.2** Garantir que ao clicar em um link da sidebar mobile, ela fecha
- [X] **T15.3** Testar responsividade em todas as telas (320px a 1440px)

#### [X] T16. Modal de Confirmação de Exclusão (JavaScript)

- [X] **T16.1** Criar componente `templates/components/modal_confirm.html`
  - Modal genérico reutilizável via `{% include %}` com variáveis de contexto
  - JavaScript vanilla para abrir/fechar modal
- [X] **T16.2** Integrar modal nas views de exclusão (contas, categorias, transações)
  - Substituir página de confirmação por modal inline na lista
- [X] **T16.3** Testar fluxo de exclusão com modal em todas as entidades

#### [X] T17. Refinamentos Visuais

- [X] **T17.1** Adicionar ícones SVG inline na sidebar (Dashboard, Contas, Categorias, etc.)
- [X] **T17.2** Formatar valores monetários como `R$ 1.234,56` nos templates
  - Criar template filter customizado `currency_brl` ou usar `floatformat` + formatação
- [X] **T17.3** Adicionar badges de tipo nas categorias (verde "Entrada", vermelho "Saída")
- [X] **T17.4** Estilizar paginação da listagem de transações
  - Botões Previous/Next com estilo do Design System
- [X] **T17.5** Adicionar animação de fade nas mensagens de feedback (auto-dismiss em 5s)
- [X] **T17.6** Revisar consistência visual de todas as telas com o Design System
  - Verificar espaçamentos, cores, bordas, fontes
- [X] **T17.7** Adicionar estados de hover e focus em todos os elementos interativos
- [X] **T17.8** Garantir que a landing page não é acessível por usuários logados (redirect)

---

### [X] Sprint 7 — Polimento e Preparação para Produção

#### [X] T18. Validações e Segurança

- [X] **T18.1** Garantir que todas as views autenticadas usam `LoginRequiredMixin`
- [X] **T18.2** Garantir que todas as queries filtram por `user=request.user`
  - Testar acesso direto a URLs de outro usuário (deve retornar 404)
- [X] **T18.3** Validar que valor de transação é sempre positivo no form
- [X] **T18.4** Validar que transação só aceita categorias do mesmo tipo (income/expense)
- [X] **T18.5** Adicionar `{% csrf_token %}` em todos os formulários (verificar)
- [X] **T18.6** Configurar `SECURE_BROWSER_XSS_FILTER = True` e `X_CONTENT_TYPE_OPTIONS` no settings

#### [X] T19. Template Filters e Helpers

- [X] **T19.1** Criar `templatetags/` em uma app (ex: `core` ou app dedicada)
  - Criar `format_filters.py` com filtro `brl_currency` para formatar Decimal → `R$ X.XXX,XX`
- [X] **T19.2** Criar filtro `active_link` para sidebar (marca item ativo por URL)
- [X] **T19.3** Registrar templatetags e usar em todos os templates relevantes

#### [X] T20. README e Documentação

- [X] **T20.1** Criar `README.md` com:
  - Descrição do projeto
  - Stack tecnológica
  - Instruções de instalação e setup local
  - Comandos úteis (runserver, migrate, createsuperuser)
  - Estrutura de diretórios
- [X] **T20.2** Documentar variáveis de settings que podem ser customizadas

---

### Sprint 8 — Agente de IA de Análise Financeira

> Referência: **RF09** e seção **8.5** do `PRD.md`. Toda a lógica fica na app `ai/`.
> Regra transversal: **nenhuma tool do agente pode acessar dados de um usuário diferente do que foi fixado no servidor.**
> Antes de escrever código do LangChain, consultar a documentação vigente via MCP context7 — não assumir APIs de memória.

#### T24. Setup da app `ai` e dependências

- [X] **T24.1** Adicionar dependências ao `requirements.txt`
  - `langchain` (1.0+), `langchain-deepseek`, `python-dotenv`
  - Gravar o arquivo em **UTF-8 sem BOM** (UTF-16 quebra o `pip install` no container)
  - Instalado e fixado: `langchain==1.3.14`, `langchain-deepseek==1.1.0`, `python-dotenv==1.2.2`
- [X] **T24.2** Criar a app: `python manage.py startapp ai`
  - Registrar `'ai'` em `INSTALLED_APPS` no `core/settings.py`
- [X] **T24.3** Configurar carregamento de variáveis de ambiente
  - `load_dotenv()` no topo de `core/settings.py`
  - Criar `.env.example` com as chaves esperadas (sem valores reais)
  - Confirmar que `.env` já está no `.gitignore`
- [X] **T24.4** Adicionar as settings do agente em `core/settings.py`
  - `DEEPSEEK_API_KEY` (do ambiente, default vazio)
  - `DEEPSEEK_MODEL` (default `'deepseek-chat'`)
  - `AI_ANALYSIS_ENABLED` (default `True`, forçado a `False` se não houver chave)
  - `AI_ANALYSIS_MIN_INTERVAL_MINUTES` (default `15`)
  - `AI_AGENT_TIMEOUT_SECONDS` (default `60`)
  - `AI_AGENT_MAX_ITERATIONS` (default `10`)
  - `AI_ANALYSIS_MONTHS_WINDOW` (default `6`)
- [X] **T24.5** Repassar a chave ao container
  - Adicionar `env_file: .env` ao serviço `web` no `docker-compose.yml`
  - Documentar que sem `.env` a funcionalidade sobe desligada
- [ ] **T24.6** Validar conexão mínima com a API DeepSeek
  - Chamada única de teste via `python manage.py shell`, confirmando credencial e nome do modelo
  - **Bloqueado:** depende de uma `DEEPSEEK_API_KEY` válida no `.env`

#### T25. Model `AIAnalysis` e persistência

- [X] **T25.1** Criar o model `AIAnalysis` em `ai/models.py`
  - `user = ForeignKey(User, on_delete=CASCADE, related_name='ai_analyses')`
  - `status = CharField(max_length=10, choices=STATUS_CHOICES)` — `success`, `error`
  - `summary = TextField(blank=True)`
  - `insights = JSONField(default=list, blank=True)`
  - `tips = JSONField(default=list, blank=True)`
  - `health_score = PositiveSmallIntegerField(null=True, blank=True)`
  - `health_label = CharField(max_length=20, choices=HEALTH_LABEL_CHOICES, blank=True)`
  - `period_start` / `period_end` = `DateField(null=True, blank=True)`
  - `model_name = CharField(max_length=50, blank=True)`
  - `prompt_tokens`, `completion_tokens`, `total_tokens` = `PositiveIntegerField(default=0)`
  - `duration_ms = PositiveIntegerField(default=0)`
  - `iterations = PositiveSmallIntegerField(default=0)`
  - `error_message = TextField(blank=True)`
  - `created_at` (auto_now_add) e `updated_at` (auto_now)
- [X] **T25.2** Configurar `class Meta`
  - `ordering = ['-created_at']`
  - `indexes = [models.Index(fields=['user', '-created_at'])]`
  - `verbose_name = 'análise de IA'` e `verbose_name_plural = 'análises de IA'`
- [X] **T25.3** Implementar `__str__` e helpers de consulta
  - Manager ou classmethod `latest_success_for(user)` retornando a última análise com `status='success'`
  - Property `health_color_class` mapeando a faixa do score para a classe Tailwind (ver 9.10 do PRD)
- [X] **T25.4** Registrar no admin com `list_display`, `list_filter` e `readonly_fields`
- [X] **T25.5** Executar `makemigrations ai` e `migrate`

#### T26. Tools de acesso ao banco de dados

- [X] **T26.1** Criar `ai/tools.py` com a factory `build_tools(user)`
  - O `user` é fixado por closure/`partial`; **a assinatura exposta ao modelo nunca recebe `user_id`**
  - Todas as tools são somente-leitura e usam exclusivamente o ORM do Django
- [X] **T26.2** Tool `get_financial_summary`
  - Saldo total das contas, entradas/saídas/balanço do mês corrente, nº de contas e de transações
- [X] **T26.3** Tool `get_accounts_overview`
  - Lista de contas do usuário: nome, tipo (rótulo em PT-BR), saldo inicial e saldo atual
- [X] **T26.4** Tool `get_expenses_by_category`
  - Parâmetros: `months` (default da setting, teto de 24)
  - Agrupamento por categoria com total e percentual sobre as saídas do período
- [X] **T26.5** Tool `get_income_by_category`
  - Mesma estrutura da anterior, para entradas
- [X] **T26.6** Tool `get_monthly_totals`
  - Série dos últimos N meses com entradas, saídas e balanço por mês
- [X] **T26.7** Tool `get_recent_transactions`
  - Parâmetros: `limit` (default 20, teto 50); retorna data, descrição, categoria, conta, tipo e valor
- [X] **T26.8** Tool `get_largest_expenses`
  - Maiores saídas do período, com teto de itens
- [X] **T26.9** Padronizar serialização dos retornos
  - `Decimal` convertido para `float`/`str` antes de devolver ao modelo
  - Datas em ISO 8601; nenhum objeto Django cru no retorno
  - Validar e limitar todos os parâmetros vindos do modelo
- [X] **T26.10** Escrever docstrings descritivas em cada tool
  - São elas que o modelo lê para decidir quando chamar cada tool — devem explicar o retorno e a unidade dos valores

#### T27. Agente LangChain 1.0 + DeepSeek

- [X] **T27.1** Consultar a documentação atual do LangChain 1.0 via MCP context7 **antes de codar**
  - Tópicos: construção de agente, definição de tools, saída estruturada, configuração de modelo e limites de iteração
  - Registrar no código as APIs efetivamente usadas (evita divergência com versões antigas)
  - APIs confirmadas e documentadas no docstring de `ai/agent.py`: `create_agent`, `ToolStrategy`, `ModelCallLimitMiddleware`, `ChatDeepSeek` e `recursion_limit` no `config` do `invoke`
- [X] **T27.2** Criar `ai/prompts.py` com o system prompt do especialista em finanças pessoais
  - Papel: consultor financeiro pessoal, resposta em **português brasileiro**, linguagem simples
  - Regras: usar **somente** números vindos das tools; nunca inventar valores; declarar explicitamente quando não houver dados suficientes
  - Tom: construtivo e prático, sem julgamento moral sobre os gastos
  - Proibições: não dar recomendação de investimento específico, não prometer rentabilidade
  - Inclui as faixas do `health_score` e a mensagem de tarefa `build_analysis_request(months)`
- [X] **T27.3** Criar `ai/schemas.py` com o schema Pydantic `FinancialAnalysis`
  - `summary` (2–4 frases), `insights` (3–5 itens), `tips` (3–5 itens)
  - `health_score` (0–100) e `health_label` (`critical`/`attention`/`good`/`excellent`)
  - `period_start` e `period_end`
  - Validadores garantem `period_start <= period_end` e coerência entre score e rótulo
- [X] **T27.4** Criar `ai/agent.py` com a configuração do `ChatDeepSeek`
  - Modelo e chave vindos das settings; `temperature` baixa para reduzir variação
  - `timeout` e política de retry alinhados a `AI_AGENT_TIMEOUT_SECONDS`
- [X] **T27.5** Implementar `build_finance_agent(user)`
  - Junta modelo + `build_tools(user)` + system prompt + saída estruturada `FinancialAnalysis`
  - Aplicar o teto de iterações (`AI_AGENT_MAX_ITERATIONS`)
  - Teto aplicado em duas camadas: `ModelCallLimitMiddleware(run_limit=...)` e `recursion_limit` do grafo
- [X] **T27.6** Criar `ai/services.py` com `run_analysis_for_user(user)`
  - Verificar `AI_ANALYSIS_ENABLED` e presença da chave antes de executar
  - Invocar o agente, medir duração, capturar tokens e nº de iterações
  - Persistir `AIAnalysis` com `status='success'` e os campos da saída estruturada
- [X] **T27.7** Implementar o tratamento de erros do serviço
  - `try/except` abrangente: rede, timeout, credencial inválida, limite de requisições, saída fora do schema
  - Persistir `AIAnalysis` com `status='error'` e `error_message`; registrar no logger da app
  - Nunca propagar exceção para a view a ponto de quebrar o dashboard
- [X] **T27.8** Implementar o controle de intervalo mínimo entre gerações
  - Função utilitária que verifica a última análise do usuário contra `AI_ANALYSIS_MIN_INTERVAL_MINUTES`
  - `cooldown_remaining_minutes(user)` e `can_generate_analysis(user)`; execuções com erro também contam
- [X] **T27.9** Garantir que a chave de API nunca apareça em log, mensagem de erro ou template
  - `error_message` usa apenas textos fixos; o log passa por `_redact()`, que remove a chave

#### T28. Interface: dashboard, histórico e geração sob demanda

- [ ] **T28.1** Criar `templates/components/ai_insight_card.html`
  - Card com borda superior violet, título "Análise Inteligente" com ícone SVG inline
  - Indicador de saúde (score + badge colorido por faixa), resumo, lista de insights e de dicas
  - Data de geração formatada e link para o histórico
  - Seguir o snippet da seção 9.10 do PRD
- [ ] **T28.2** Incluir a última análise no contexto da `DashboardView` (`core/views.py`)
  - `latest_ai_analysis` = última análise com `status='success'` do `request.user`
  - Consulta protegida por `try/except` para não derrubar o dashboard
- [ ] **T28.3** Implementar os estados alternativos do card
  - Vazio: usuário sem nenhuma análise → chamada para gerar a primeira
  - Erro: última execução falhou → mensagem amigável e botão para tentar de novo
  - Desligado (`AI_ANALYSIS_ENABLED=False`): card não é renderizado
- [ ] **T28.4** Criar `GenerateAnalysisView` (POST) em `ai/views.py`
  - `LoginRequiredMixin`; aceitar apenas POST com `{% csrf_token %}`
  - Bloquear se o intervalo mínimo não foi respeitado (mensagem de alerta com o tempo restante)
  - Chamar `run_analysis_for_user(request.user)` e redirecionar ao dashboard com `messages`
- [ ] **T28.5** Adicionar estado de carregamento no botão (JavaScript vanilla)
  - Desabilitar o botão e exibir spinner/texto "Analisando..." no submit, evitando duplo envio
- [ ] **T28.6** Criar `AnalysisListView` (histórico)
  - `LoginRequiredMixin` + `ListView`, `get_queryset()` filtrando por `user=self.request.user`
  - Paginação de 10 por página
- [ ] **T28.7** Criar `AnalysisDetailView`
  - `LoginRequiredMixin` + `DetailView`, queryset filtrado por usuário (acesso a análise de outro → 404)
- [ ] **T28.8** Criar `templates/ai/analysis_list.html` e `templates/ai/analysis_detail.html`
  - Estender `base_app.html` e seguir o Design System
  - Estado vazio amigável na listagem
- [ ] **T28.9** Criar `ai/urls.py` com `app_name = 'ai'` e incluir em `core/urls.py`
  - `analises/` → histórico, `analises/<pk>/` → detalhe, `analises/gerar/` → geração (POST)
- [ ] **T28.10** Adicionar "Análises" na sidebar
  - Ícone SVG inline, estado ativo via filtro `active_link`
- [ ] **T28.11** Aplicar as cores do indicador de saúde conforme a tabela da seção 9.10 do PRD

#### T29. Geração em lote (management command)

- [ ] **T29.1** Criar `ai/management/commands/run_ai_analysis.py`
  - Sem argumentos: gera uma análise para **cada usuário ativo**, usando apenas os dados de cada um
- [ ] **T29.2** Adicionar as opções do comando
  - `--user <email>` para um único usuário
  - `--skip-empty` para pular usuários sem transações
  - `--dry-run` para listar quem seria processado sem chamar a API
- [ ] **T29.3** Isolar falhas por usuário
  - Erro em um usuário não interrompe os demais; cada falha vira um `AIAnalysis` com `status='error'`
- [ ] **T29.4** Exibir resumo ao final
  - Total processado, sucessos, falhas e tempo total, com `self.stdout.write` colorido
- [ ] **T29.5** Documentar o comando no README (execução local e via `docker compose exec`)

#### T30. Testes

- [ ] **T30.1** Criar dublê do modelo de IA em `conftest.py`
  - Fake/stub que devolve uma `FinancialAnalysis` fixa — **nenhum teste chama a API real**
  - Fixture de usuário com transações em categorias variadas
- [ ] **T30.2** Testes das tools: valores corretos
  - Somatórios, percentuais e agrupamentos conferem com os dados criados na fixture
- [ ] **T30.3** Testes das tools: **isolamento entre usuários** (bloqueante)
  - Tools construídas para o usuário A nunca retornam dados do usuário B
  - Nenhuma tool aceita parâmetro que permita trocar de usuário
- [ ] **T30.4** Testes do serviço
  - Sucesso: cria `AIAnalysis` com `status='success'` e campos preenchidos
  - Falha simulada na API: cria `AIAnalysis` com `status='error'` e mensagem, sem levantar exceção
  - Feature flag desligada: não chama o agente
- [ ] **T30.5** Testes do dashboard
  - Card exibe a última análise bem-sucedida do próprio usuário
  - Usuário sem análises vê o estado vazio
  - Análise de outro usuário nunca aparece
- [ ] **T30.6** Testes das views de histórico
  - Listagem só traz análises do usuário logado
  - Detalhe de análise de outro usuário retorna 404
  - Rotas exigem login
- [ ] **T30.7** Teste do intervalo mínimo entre gerações
  - Segunda solicitação dentro da janela é bloqueada com mensagem, sem chamar o agente
- [ ] **T30.8** Teste do management command
  - Gera uma análise por usuário ativo; falha de um usuário não interrompe os demais
- [ ] **T30.9** Rodar a suíte completa e garantir que os testes anteriores continuam passando

#### T31. Documentação

- [ ] **T31.1** Adicionar seção "Agente de IA" no `README.md`
  - Como obter e configurar `DEEPSEEK_API_KEY`, variáveis disponíveis, comandos de geração
  - Aviso de custo: cada análise consome tokens da API
- [ ] **T31.2** Versionar o `.env.example` com todas as chaves esperadas
- [ ] **T31.3** Atualizar `CLAUDE.md` com a app `ai` (domínio, convenções e regra de isolamento por usuário)
- [ ] **T31.4** Atualizar `relatorio.md` com a nova app, o model `AIAnalysis` e o fluxo do agente

---

### Sprint 9 — Testes

#### [X] T21. Setup de Testes

- [X] **T21.1** Configurar `pytest` e `pytest-django` no projeto
  - Adicionar ao `requirements.txt`
  - Criar `pytest.ini` ou `pyproject.toml` com configuração Django
- [X] **T21.2** Criar fixtures base: usuário de teste, conta, categoria, transação

#### T22. Testes por App

- [X] **T22.1** Testes `users`: cadastro, login, login com e-mail inválido, logout
- [X] **T22.2** Testes `profiles`: edição de perfil, criação automática via signal
- [X] **T22.3** Testes `accounts`: CRUD completo, saldo inicial = saldo atual na criação
- [X] **T22.4** Testes `categories`: CRUD, categorias padrão via signal, proteção de exclusão
- [X] **T22.5** Testes `transactions`: CRUD, atualização de saldo, filtros
- [X] **T22.6** Testes `dashboard`: cálculos corretos de saldos e totais mensais
- [X] **T22.7** Testes de segurança: acesso a dados de outro usuário retorna 404

---

### [X] Sprint 10 — Docker
#### [X] T23. Dockerização

- [X] **T23.1** Criar `Dockerfile` com Python 3.12 + pip install de requirements
- [X] **T23.2** Criar `docker-compose.yml` com serviço web
- [X] **T23.3** Configurar volume para persistir db.sqlite3
- [X] **T23.4** Documentar no README os comandos Docker
- [X] **T23.5** Testar build e execução completa via Docker
