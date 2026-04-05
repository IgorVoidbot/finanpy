# Agentes de IA — Finanpy

Agentes especializados na stack do projeto para auxiliar no desenvolvimento. Cada agente conhece as convenções, o design system e a arquitetura do Finanpy.

---

## Índice

| Agente | Arquivo | Especialidade |
|---|---|---|
| [Backend](#backend) | [backend.md](./backend.md) | Django models, CBVs, forms, signals, migrations |
| [Frontend](#frontend) | [frontend.md](./frontend.md) | Django Template Language, TailwindCSS, components |
| [QA](#qa) | [qa.md](./qa.md) | Testes via Playwright, verificação de design e fluxos |

---

## Backend

**Arquivo:** `agents/backend.md`
**MCP:** context7 (documentação Django)

Responsável por toda a camada de dados e lógica de negócio:

- Criação e manutenção de **models** Django (com `created_at`, `updated_at`, campos monetários)
- Implementação de **class-based views** com `LoginRequiredMixin` e isolamento por usuário
- **Forms**, validações e `form_valid()` para associar o `request.user`
- **Signals** (`post_save`) para criação automática de `Profile` e categorias padrão
- Configuração de **URLs** por app
- Geração de **migrations**
- Regras de negócio críticas: recálculo de `current_balance` ao criar/editar/excluir `Transaction`

**Quando usar:** sempre que a tarefa envolver código Python — models, views, forms, signals ou qualquer lógica de servidor.

---

## Frontend

**Arquivo:** `agents/frontend.md`
**MCP:** context7 (documentação TailwindCSS e Django Template Language)

Responsável pela camada de apresentação:

- Criação de **templates HTML** com Django Template Language
- Aplicação do **design system**: tema escuro, paleta emerald/violet/rose, tipografia
- **Components reutilizáveis**: navbar, sidebar, cards, modais de confirmação, mensagens de feedback
- **Formulários** renderizados com exibição de erros por campo
- **Layout responsivo**: sidebar oculta em mobile, grids adaptativos
- Tabelas, filtros e listagens

**Quando usar:** sempre que a tarefa envolver criar ou modificar arquivos `.html` em `templates/`.

---

## QA

**Arquivo:** `agents/qa.md`
**MCP:** Playwright (navegação e interação com o sistema rodando)

Responsável por verificar se o sistema funciona corretamente no navegador:

- Testa **fluxos completos** de usuário: cadastro, login, CRUD de contas, categorias, transações, dashboard
- Verifica **comportamento das views**: redirecionamentos, mensagens de sucesso/erro, dados exibidos
- Confere **conformidade com o design system**: cores, componentes, responsividade
- Valida **regras de negócio**: recálculo de saldo, impedimento de exclusão de categoria com transações
- Verifica **segurança básica**: rotas protegidas, isolamento de dados por usuário

**Quando usar:** após a implementação de qualquer funcionalidade ou correção de bug, para validar que tudo está funcionando e visualmente correto. Requer o servidor rodando em `http://127.0.0.1:8000`.
