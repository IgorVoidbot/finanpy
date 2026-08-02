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

# Gerar as análises de IA em lote (exige DEEPSEEK_API_KEY no .env)
python manage.py run_ai_analysis
python manage.py run_ai_analysis --dry-run
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
| `ai/` | Agente de análise financeira (LangChain 1.0 + DeepSeek); model `AIAnalysis` |

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
 ├── Transaction (FK) → também FK para Account e Category
 └── AIAnalysis (FK) — análises de IA; status: success, error
```

`Category` tem `unique_together = ['user', 'name', 'transaction_type']`.
`Transaction` ordering padrão: `['-date', '-created_at']`.
`AIAnalysis` também é FK para `User` (`related_name='ai_analyses'`), ordering `['-created_at']`.

## App `ai` — agente de análise financeira

Agente LangChain 1.0 com a API da DeepSeek que analisa os dados de **um usuário por execução** e grava o resultado em `AIAnalysis` (inclusive as falhas, com `status='error'`).

| Módulo | Responsabilidade |
|---|---|
| `tools.py` | `build_tools(user)` — tools de leitura, somente ORM, escopadas por closure |
| `prompts.py` | System prompt do consultor financeiro, em PT-BR |
| `schemas.py` | `FinancialAnalysis` (Pydantic) — saída estruturada |
| `agent.py` | `build_finance_agent(user)` — modelo + tools + prompt + teto de iterações |
| `services.py` | `run_analysis_for_user(user)` — executa, mede, persiste, trata erro |
| `management/commands/run_ai_analysis.py` | Geração em lote para os usuários ativos |

Regras obrigatórias desta app:

- **Isolamento por usuário é bloqueante.** O `user` é fixado no servidor por closure; a assinatura exposta ao modelo **nunca** contém `user_id`. Nenhuma tool aceita SQL livre — todo acesso é ORM com `filter(user=...)`.
- Todo parâmetro vindo do modelo é validado e tem teto (`months`, `limit`).
- **Nenhuma falha da IA pode quebrar o dashboard**: `run_analysis_for_user()` nunca propaga exceção, e a montagem do contexto do card na `DashboardView` fica dentro de `try/except`.
- A chave da API nunca aparece em log, mensagem de erro ou template — `error_message` usa textos fixos.
- Antes de mexer em código do LangChain, **consultar a documentação vigente via MCP context7** — não assumir APIs de memória.
- Testes nunca chamam a API real: use o `FakeAgent` e as fixtures `fake_agent` / `ai_enabled` do `conftest.py`.

Sem `DEEPSEEK_API_KEY` no ambiente, `AI_ANALYSIS_ENABLED` cai para `False` e a funcionalidade some da interface sem afetar nenhum outro fluxo.

## Design system

Tema escuro com TailwindCSS via CDN. Classes de referência:

- Background body: `bg-gray-950` / Cards: `bg-gray-900` / Inputs: `bg-gray-800`
- Accent primário (entradas, botão salvar): `bg-emerald-500`
- Perigo (exclusão, saídas): `bg-rose-500`
- Accent secundário (badges, links ativos): `bg-violet-500`
- Texto principal: `text-gray-100` / Secundário: `text-gray-400`

Consulte `docs/design-system.md` para snippets completos de botões, inputs, cards, navbar, sidebar e modais.
