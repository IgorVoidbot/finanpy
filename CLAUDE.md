# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos essenciais

```bash
# Ativar ambiente virtual
source .venv/bin/activate          # Linux/Mac
.venv\Scripts\activate             # Windows

# Rodar o servidor de desenvolvimento
python manage.py runserver

# Criar e aplicar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar testes
python manage.py test
python manage.py test users        # testes de um app específico
```

## Arquitetura

Projeto Django full-stack chamado **Finanpy**. O módulo de configuração global é `core/` (settings, urls, wsgi, asgi). Cada domínio vive em sua própria app:

| App | Domínio |
|---|---|
| `users/` | Model de usuário customizado (`AbstractUser`), login via e-mail |
| `profiles/` | Perfil do usuário, criado via signal `post_save` no User |
| `accounts/` | Contas bancárias; `current_balance` recalculado a cada transação |
| `categories/` | Categorias de transações; categorias padrão criadas via signal no User |
| `transactions/` | Transações financeiras; atualiza `current_balance` do Account associado |

Templates globais ficam em `templates/` na raiz (não dentro das apps). A URL raiz é configurada em `core/urls.py`; cada app deve ter seu próprio `urls.py` incluído via `include()`.

## Convenções obrigatórias

- **Código em inglês**, interface do usuário em **português brasileiro**
- **Aspas simples** em todo o código Python
- **Class-based views** (CBVs) com `LoginRequiredMixin` em todas as views autenticadas
- Todos os models devem ter `created_at = DateTimeField(auto_now_add=True)` e `updated_at = DateTimeField(auto_now=True)`
- Valores monetários: `DecimalField(max_digits=10, decimal_places=2)`
- Toda query de listagem deve filtrar por `user=request.user` — nunca expor dados de outros usuários
- Ao excluir/editar uma `Transaction`, recalcular `current_balance` da `Account` associada

## Modelo de dados (resumo)

```
User (AbstractUser, USERNAME_FIELD='email')
 ├── Profile (OneToOne)
 ├── Account (FK) — tipos: checking, savings, wallet, investment
 ├── Category (FK) — tipos: income, expense
 └── Transaction (FK) → também FK para Account e Category
```

`Category` tem `unique_together = ['user', 'name', 'transaction_type']`.
`Transaction` ordering padrão: `['-date', '-created_at']`.

## Design system

Tema escuro com TailwindCSS via CDN. Classes de referência:

- Background body: `bg-gray-950` / Cards: `bg-gray-900` / Inputs: `bg-gray-800`
- Accent primário (entradas, botão salvar): `bg-emerald-500`
- Perigo (exclusão, saídas): `bg-rose-500`
- Accent secundário (badges, links ativos): `bg-violet-500`
- Texto principal: `text-gray-100` / Secundário: `text-gray-400`

Consulte `docs/design-system.md` para snippets completos de botões, inputs, cards, navbar, sidebar e modais.
