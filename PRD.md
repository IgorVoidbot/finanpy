# PRD — Finanpy: Sistema de Gestão de Finanças Pessoais

> **Versão:** 1.1  
> **Data:** 02/08/2026 (v1.0 em 05/04/2026)  
> **Autor:** Igor  
> **Status:** Draft  
> **Alterações da v1.1:** adição do Agente de IA de análise financeira (RF09), construído com LangChain 1.0 + DeepSeek

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Sobre o Produto](#2-sobre-o-produto)
3. [Propósito](#3-propósito)
4. [Público-Alvo](#4-público-alvo)
5. [Objetivos](#5-objetivos)
6. [Requisitos Funcionais](#6-requisitos-funcionais)
7. [Requisitos Não-Funcionais](#7-requisitos-não-funcionais)
8. [Arquitetura Técnica](#8-arquitetura-técnica)
9. [Design System](#9-design-system)
10. [User Stories](#10-user-stories)
11. [Métricas de Sucesso](#11-métricas-de-sucesso)
12. [Riscos e Mitigações](#12-riscos-e-mitigações)
13. [Lista de Tarefas (Sprints)](#13-lista-de-tarefas-sprints)

---

## 1. Visão Geral

O **Finanpy** é um sistema web de gestão de finanças pessoais desenvolvido com Django full-stack. Permite que usuários registrem contas bancárias, categorizem transações (entradas e saídas) e acompanhem sua saúde financeira por meio de um dashboard centralizado. O projeto prioriza simplicidade, sem over-engineering, utilizando os recursos nativos do Django sempre que possível.

---

## 2. Sobre o Produto

| Atributo | Descrição |
|---|---|
| **Nome** | Finanpy |
| **Tipo** | Aplicação web full-stack |
| **Framework** | Django (Python) |
| **Frontend** | Django Template Language + TailwindCSS |
| **Banco de dados** | SQLite (padrão Django) |
| **Autenticação** | Sistema nativo do Django (login via e-mail) |
| **Idioma da interface** | Português brasileiro |
| **Idioma do código** | Inglês |

---

## 3. Propósito

Oferecer uma ferramenta simples, funcional e visualmente agradável para que pessoas possam organizar suas finanças pessoais — registrando contas, categorias e transações — sem a complexidade de ferramentas corporativas. O Finanpy visa ser o ponto de partida para o controle financeiro de quem nunca usou ou abandonou planilhas.

---

## 4. Público-Alvo

- **Jovens adultos (18-35 anos)** que estão começando a organizar suas finanças.
- **Estudantes e profissionais** que desejam controle básico de entradas e saídas.
- **Usuários não-técnicos** que precisam de uma interface intuitiva, sem jargão financeiro excessivo.
- **Pessoas que abandonaram planilhas** por achar complexo ou pouco visual.

---

## 5. Objetivos

| # | Objetivo | Métrica de validação |
|---|---|---|
| O1 | Permitir cadastro e login de usuários via e-mail | Fluxo completo funcional |
| O2 | Gerenciar contas bancárias (CRUD) | Usuário consegue criar, editar, listar e excluir contas |
| O3 | Gerenciar categorias de transações (CRUD) | Categorias criadas e atribuídas a transações |
| O4 | Registrar transações de entrada e saída (CRUD) | Transações vinculadas a conta + categoria |
| O5 | Exibir dashboard com resumo financeiro | Dashboard com saldo, totais de entrada/saída |
| O6 | Oferecer landing page pública | Página de apresentação com acesso a cadastro/login |
| O7 | Entregar insights e dicas financeiras geradas por IA | Última análise do agente visível no dashboard, gerada só com dados do próprio usuário |

---

## 6. Requisitos Funcionais

### RF01 — Landing Page (pública)
- Página de apresentação do sistema.
- Botões de "Cadastre-se" e "Entrar".
- Sem acesso a funcionalidades internas.

### RF02 — Cadastro de Usuário
- Formulário com: nome, e-mail, senha, confirmação de senha.
- Validação de e-mail único.
- Login automático após cadastro (redireciona ao dashboard).

### RF03 — Login / Logout
- Login via **e-mail + senha** (não username).
- Redirecionamento ao dashboard após login.
- Logout com redirecionamento à landing page.

### RF04 — Perfil do Usuário
- Edição de nome e e-mail.
- Dados exibidos no menu do sistema (nome do usuário).

### RF05 — Gerenciamento de Contas Bancárias
- CRUD completo (criar, listar, editar, excluir).
- Campos: nome da conta, tipo (corrente, poupança, carteira, investimento), saldo inicial.
- Saldo atualizado automaticamente conforme transações.
- Cada conta pertence exclusivamente ao usuário logado.

### RF06 — Gerenciamento de Categorias
- CRUD completo.
- Campos: nome, tipo (entrada ou saída), ícone/cor (opcional).
- Categorias vinculadas ao usuário.
- Categorias padrão criadas automaticamente no cadastro (ex: Salário, Alimentação, Transporte).

### RF07 — Gerenciamento de Transações
- CRUD completo.
- Campos: descrição, valor, data, tipo (entrada/saída), conta, categoria.
- Listagem com filtros por período, tipo, conta e categoria.
- Ao criar/editar/excluir transação, o saldo da conta é recalculado.

### RF08 — Dashboard
- Saldo total (soma dos saldos de todas as contas).
- Total de entradas e saídas do mês corrente.
- Lista das últimas transações.
- Resumo por categoria (quanto foi gasto/recebido por categoria no mês).
- **Card da última análise do agente de IA** (ver RF09).

### RF09 — Agente de IA de Análise Financeira

Um agente de IA especializado em finanças pessoais analisa os dados do usuário (contas, categorias, transações) e produz um diagnóstico com insights e dicas práticas. Construído com **LangChain 1.0**, usando a **API da DeepSeek** como provedor de modelo. Toda a lógica vive na app `ai/`.

#### RF09.1 — Geração da análise
- O agente recebe **um usuário por execução** e trabalha exclusivamente com os dados desse usuário.
- O agente decide quais dados buscar chamando **tools de leitura do banco relacional** (ver 8.5).
- A análise é gerada em **português brasileiro**, em linguagem simples, sem jargão financeiro.
- Formas de disparo:
  1. **Sob demanda** — botão "Gerar nova análise" no dashboard (usuário logado gera a própria análise).
  2. **Em lote** — management command `python manage.py run_ai_analysis`, que percorre todos os usuários ativos e gera uma análise individual para cada um.

#### RF09.2 — Conteúdo da análise
Cada análise contém:
- **Resumo** (`summary`) — parágrafo curto com o diagnóstico geral do período.
- **Insights** (`insights`) — lista de observações objetivas extraídas dos dados (ex.: "Alimentação consumiu 38% das saídas do mês, acima dos 25% do mês anterior").
- **Dicas** (`tips`) — lista de recomendações acionáveis (ex.: "Estabeleça um teto de R$ 800 para Alimentação no próximo mês").
- **Indicador de saúde financeira** (`health_score`) — nota de 0 a 100 com um rótulo (`critical`, `attention`, `good`, `excellent`).
- **Período analisado** (`period_start`, `period_end`).

#### RF09.3 — Persistência
- Toda análise é gravada na tabela `ai_analysis` (model `AIAnalysis`), incluindo as que falharem (com `status='error'` e a mensagem de erro).
- O histórico é preservado — análises antigas **não** são sobrescritas.
- Metadados de execução são gravados junto: modelo usado, tokens consumidos, duração e número de iterações do agente.

#### RF09.4 — Exibição
- O dashboard exibe a **última análise bem-sucedida** do usuário logado, em card destacado, com resumo, insights, dicas, indicador de saúde e data de geração.
- Estado vazio: se o usuário nunca gerou uma análise, o card exibe uma chamada para gerar a primeira.
- Estado sem dados: se o usuário não tem transações suficientes, a análise informa isso em vez de inventar conclusões.
- Página de **histórico** (`/analises/`) lista todas as análises do usuário, com detalhe individual.

#### RF09.5 — Isolamento por usuário (crítico)
- As análises são **individuais e privadas**: nenhum usuário acessa a análise de outro.
- As tools do agente recebem o `user_id` **fixado no servidor** no momento da construção do agente — o modelo de IA **nunca** informa de qual usuário quer os dados.
- Nenhuma tool aceita SQL livre gerado pelo modelo. Todo acesso ao banco passa pelo ORM do Django, sempre com `filter(user=...)`.

#### RF09.6 — Tratamento de falhas
- Falha de rede, chave inválida, timeout ou estouro de limite de requisições **não** podem quebrar o dashboard: o card cai no estado vazio/erro e o restante da página continua funcional.
- Erros são registrados na própria tabela de análises e no log da aplicação.
- Se a chave da API não estiver configurada, a funcionalidade fica desligada de forma silenciosa (feature flag `AI_ANALYSIS_ENABLED`).

#### RF09.7 — Limites de uso
- Intervalo mínimo entre gerações sob demanda por usuário (padrão: 15 minutos), para conter custo de API e uso abusivo.
- Timeout por execução (padrão: 60s) e teto de iterações do agente (padrão: 10).

### Flowchart — Fluxos de UX

```mermaid
flowchart TD
    A[Usuário acessa o site] --> B{Está autenticado?}
    B -- Não --> C[Landing Page]
    C --> D[Cadastre-se]
    C --> E[Login]
    D --> F[Formulário de Cadastro]
    F --> G[Validação dos dados]
    G -- Erro --> F
    G -- Sucesso --> H[Login automático]
    H --> I[Dashboard]
    E --> J[Formulário de Login via E-mail]
    J --> K[Validação de credenciais]
    K -- Erro --> J
    K -- Sucesso --> I
    B -- Sim --> I

    I --> L[Menu Principal]
    L --> M[Contas Bancárias]
    L --> N[Categorias]
    L --> O[Transações]
    L --> P[Perfil]
    L --> R[Análises de IA]
    L --> Q[Logout]

    M --> M1[Listar Contas]
    M1 --> M2[Criar Conta]
    M1 --> M3[Editar Conta]
    M1 --> M4[Excluir Conta]

    N --> N1[Listar Categorias]
    N1 --> N2[Criar Categoria]
    N1 --> N3[Editar Categoria]
    N1 --> N4[Excluir Categoria]

    O --> O1[Listar Transações]
    O1 --> O2[Criar Transação]
    O1 --> O3[Editar Transação]
    O1 --> O4[Excluir Transação]
    O2 --> O5[Recalcular saldo da conta]
    O3 --> O5
    O4 --> O5

    P --> P1[Editar Nome / E-mail]

    R --> R1[Histórico de Análises]
    R1 --> R2[Detalhe da Análise]
    I --> R3[Card da última análise no Dashboard]
    R3 --> R4[Gerar nova análise]
    R4 --> R5[Agente de IA consulta dados do usuário via tools]
    R5 --> R6[Salva AIAnalysis no banco]
    R6 --> I

    Q --> C
```

---

## 7. Requisitos Não-Funcionais

| # | Requisito | Detalhe |
|---|---|---|
| RNF01 | **Responsividade** | Interface funcional em desktop, tablet e mobile |
| RNF02 | **Performance** | Páginas carregam em < 2s com SQLite local |
| RNF03 | **Segurança** | CSRF protection (nativo Django), senhas com hash, acesso restrito por login |
| RNF04 | **Padrão de código** | PEP08, aspas simples, código em inglês |
| RNF05 | **Isolamento de domínios** | Cada entidade em sua própria Django app |
| RNF06 | **Auditoria básica** | Campos `created_at` e `updated_at` em todos os models |
| RNF07 | **Simplicidade** | Sem over-engineering; usar recursos nativos do Django |
| RNF08 | **Banco de dados** | SQLite padrão do Django |
| RNF09 | **Interface em PT-BR** | Toda informação ao usuário em português brasileiro |
| RNF10 | **Class Based Views** | Usar CBVs sempre que possível |
| RNF11 | **Segredos fora do repositório** | `DEEPSEEK_API_KEY` lida de variável de ambiente / `.env`; nunca versionada |
| RNF12 | **Isolamento de dados na IA** | Tools do agente sempre filtram por um `user_id` fixado no servidor; sem SQL livre gerado pelo modelo |
| RNF13 | **Degradação graciosa da IA** | Indisponibilidade da API DeepSeek não pode quebrar dashboard nem nenhum fluxo existente |
| RNF14 | **Testes sem chamadas externas** | Suíte de testes nunca chama a API real — modelo e agente são substituídos por dublês |
| RNF15 | **Custo previsível** | Intervalo mínimo entre análises por usuário, timeout e teto de iterações configuráveis |
| RNF16 | **Documentação de API atual** | Implementação do agente deve seguir a documentação vigente do LangChain 1.0 (consultada via MCP context7), não conhecimento prévio |

---

## 8. Arquitetura Técnica

### 8.1 Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.13+ |
| Framework backend | Django 5+ |
| Frontend | Django Template Language |
| Estilização | TailwindCSS (via CDN ou standalone CLI) |
| Banco de dados | SQLite3 |
| Servidor de dev | `manage.py runserver` |
| Autenticação | `django.contrib.auth` (customizado para login via e-mail) |
| Gerenciamento de pacotes | pip + requirements.txt |
| Agente de IA | LangChain 1.0 (`langchain`, `langchain-core`) |
| Provedor de LLM | DeepSeek via `langchain-deepseek` (`ChatDeepSeek`) |
| Configuração de segredos | variáveis de ambiente + `python-dotenv` |
| Containerização | Docker + Docker Compose |

### 8.2 Estrutura de Diretórios

```
finanpy/
├── accounts/          # Contas bancárias do usuário
├── ai/                # Agente de IA (LangChain 1.0 + DeepSeek)
│   ├── models.py              # AIAnalysis
│   ├── agent.py               # Construção do agente LangChain
│   ├── tools.py               # Tools de leitura do banco (escopadas por usuário)
│   ├── prompts.py             # System prompt do agente financeiro
│   ├── schemas.py             # Schema Pydantic da saída estruturada
│   ├── services.py            # Orquestração: executar agente e persistir análise
│   ├── views.py               # Histórico, detalhe e geração sob demanda
│   ├── urls.py                # analises/*
│   ├── admin.py
│   ├── apps.py
│   ├── management/commands/
│   │   └── run_ai_analysis.py # Geração em lote para todos os usuários
│   └── migrations/
├── categories/        # Categorias de transações
├── core/              # Configurações globais (settings, urls, wsgi, asgi)
├── profiles/          # Perfil do usuário
├── transactions/      # Transações financeiras
├── users/             # Model de usuário customizado + autenticação
├── templates/         # Templates globais (base, landing, components)
│   ├── base.html
│   ├── components/
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── card.html
│   │   ├── modal_confirm.html
│   │   ├── ai_insight_card.html   # Card da última análise (dashboard)
│   │   └── messages.html
│   ├── ai/
│   │   ├── analysis_list.html
│   │   └── analysis_detail.html
│   ├── landing.html
│   └── dashboard.html
├── static/            # Arquivos estáticos globais
│   ├── css/
│   └── js/
├── .env               # Segredos locais (fora do controle de versão)
├── db.sqlite3
├── manage.py
└── requirements.txt
```

### 8.3 Estrutura de Dados (ER Diagram)

```mermaid
erDiagram
    USER {
        int id PK
        string email UK
        string first_name
        string last_name
        string password
        boolean is_active
        datetime date_joined
        datetime created_at
        datetime updated_at
    }

    PROFILE {
        int id PK
        int user_id FK
        string display_name
        datetime created_at
        datetime updated_at
    }

    ACCOUNT {
        int id PK
        int user_id FK
        string name
        string account_type
        decimal initial_balance
        decimal current_balance
        datetime created_at
        datetime updated_at
    }

    CATEGORY {
        int id PK
        int user_id FK
        string name
        string transaction_type
        datetime created_at
        datetime updated_at
    }

    TRANSACTION {
        int id PK
        int user_id FK
        int account_id FK
        int category_id FK
        string description
        decimal amount
        string transaction_type
        date date
        datetime created_at
        datetime updated_at
    }

    AI_ANALYSIS {
        int id PK
        int user_id FK
        string status
        text summary
        json insights
        json tips
        int health_score
        string health_label
        date period_start
        date period_end
        string model_name
        int total_tokens
        int duration_ms
        int iterations
        text error_message
        datetime created_at
        datetime updated_at
    }

    USER ||--|| PROFILE : "tem"
    USER ||--o{ ACCOUNT : "possui"
    USER ||--o{ CATEGORY : "cria"
    USER ||--o{ TRANSACTION : "registra"
    USER ||--o{ AI_ANALYSIS : "recebe"
    ACCOUNT ||--o{ TRANSACTION : "pertence"
    CATEGORY ||--o{ TRANSACTION : "classifica"
```

### 8.4 Detalhamento dos Models

**User** (herda de `AbstractUser`)
- `email`: EmailField, unique, usado como USERNAME_FIELD
- `username`: removido ou ignorado no fluxo
- `created_at`: DateTimeField, auto_now_add
- `updated_at`: DateTimeField, auto_now

**Profile** (OneToOne com User)
- `user`: OneToOneField → User
- `display_name`: CharField, max 100
- `created_at` / `updated_at`

**Account**
- `user`: ForeignKey → User
- `name`: CharField, max 100
- `account_type`: CharField, choices (checking, savings, wallet, investment)
- `initial_balance`: DecimalField(10, 2), default 0
- `current_balance`: DecimalField(10, 2), default 0
- `created_at` / `updated_at`

**Category**
- `user`: ForeignKey → User
- `name`: CharField, max 50
- `transaction_type`: CharField, choices (income, expense)
- `created_at` / `updated_at`

**Transaction**
- `user`: ForeignKey → User
- `account`: ForeignKey → Account
- `category`: ForeignKey → Category
- `description`: CharField, max 200
- `amount`: DecimalField(10, 2)
- `transaction_type`: CharField, choices (income, expense)
- `date`: DateField
- `created_at` / `updated_at`

**AIAnalysis** (app `ai`)
- `user`: ForeignKey → User, `related_name='ai_analyses'`, `on_delete=CASCADE`
- `status`: CharField(10), choices (`success`, `error`) — registro é gravado nos dois casos
- `summary`: TextField — diagnóstico geral em PT-BR
- `insights`: JSONField, `default=list` — lista de strings
- `tips`: JSONField, `default=list` — lista de strings
- `health_score`: PositiveSmallIntegerField, null/blank — 0 a 100
- `health_label`: CharField(20), choices (`critical`, `attention`, `good`, `excellent`), blank
- `period_start` / `period_end`: DateField, null/blank — janela de dados analisada
- `model_name`: CharField(50) — modelo DeepSeek usado na execução
- `prompt_tokens` / `completion_tokens` / `total_tokens`: PositiveIntegerField, default 0
- `duration_ms`: PositiveIntegerField, default 0
- `iterations`: PositiveSmallIntegerField, default 0 — chamadas ao modelo no loop do agente
- `error_message`: TextField, blank — preenchido quando `status='error'`
- `created_at` / `updated_at`
- `Meta`: `ordering = ['-created_at']`, índice em `['user', '-created_at']`, `verbose_name = 'análise de IA'`

### 8.5 Arquitetura do Agente de IA

#### 8.5.1 Módulos da app `ai/`

| Módulo | Responsabilidade |
|---|---|
| `tools.py` | Tools LangChain de leitura do banco. Uma factory `build_tools(user)` devolve as tools já vinculadas ao usuário |
| `prompts.py` | System prompt do especialista em finanças pessoais (PT-BR), com regras de tom, formato e proibição de inventar dados |
| `schemas.py` | Schema Pydantic `FinancialAnalysis` usado como saída estruturada do agente |
| `agent.py` | `build_finance_agent(user)` — monta `ChatDeepSeek` + tools + prompt + saída estruturada |
| `services.py` | `run_analysis_for_user(user)` — executa o agente, mede tempo/tokens, persiste `AIAnalysis`, captura erros |
| `views.py` | `AnalysisListView`, `AnalysisDetailView`, `GenerateAnalysisView` (POST) |
| `management/commands/run_ai_analysis.py` | Geração em lote para todos os usuários ativos |

#### 8.5.2 Tools disponíveis ao agente

Todas somente-leitura, todas escopadas ao usuário fixado no servidor, todas retornando dados serializáveis (dict/list) já agregados:

| Tool | Retorno |
|---|---|
| `get_financial_summary` | Saldo total, entradas/saídas do mês, balanço, nº de contas e de transações |
| `get_accounts_overview` | Lista de contas com tipo, saldo inicial e saldo atual |
| `get_expenses_by_category` | Gastos agrupados por categoria em um período, com valor e percentual |
| `get_income_by_category` | Entradas agrupadas por categoria em um período |
| `get_monthly_totals` | Série mensal de entradas, saídas e balanço dos últimos N meses |
| `get_recent_transactions` | Últimas N transações (data, descrição, categoria, conta, tipo, valor) |
| `get_largest_expenses` | Maiores saídas de um período |

Regras de implementação das tools:
- Assinatura exposta ao modelo **nunca** inclui `user_id`; o usuário vem por closure/`partial` na factory.
- Parâmetros aceitos do modelo limitam-se a filtros inofensivos (período, quantidade, tipo), sempre validados e com teto.
- Retornos limitados em volume (ex.: máximo de 50 transações) para conter o tamanho do contexto e o custo.

#### 8.5.3 Fluxo de execução

```mermaid
sequenceDiagram
    participant U as Usuário / Command
    participant S as services.run_analysis_for_user
    participant A as Agente LangChain
    participant D as DeepSeek API
    participant T as Tools (ORM Django)
    participant DB as Banco de dados

    U->>S: solicita análise (user)
    S->>A: build_finance_agent(user) + invoke
    A->>D: mensagens + definições das tools
    D-->>A: pedido de chamada de tool
    A->>T: executa tool (escopada ao user)
    T->>DB: query ORM filtrada por user
    DB-->>T: dados agregados
    T-->>A: resultado da tool
    A->>D: resultado da tool
    D-->>A: saída estruturada final
    A-->>S: FinancialAnalysis
    S->>DB: grava AIAnalysis (success ou error)
    S-->>U: análise persistida
```

#### 8.5.4 Saída estruturada

O agente devolve um objeto validado pelo schema `FinancialAnalysis`:

| Campo | Tipo | Regra |
|---|---|---|
| `summary` | str | 2 a 4 frases |
| `insights` | list[str] | 3 a 5 itens |
| `tips` | list[str] | 3 a 5 itens, acionáveis |
| `health_score` | int | 0 a 100 |
| `health_label` | enum | `critical`, `attention`, `good`, `excellent` |
| `period_start` / `period_end` | date | janela efetivamente analisada |

#### 8.5.5 Configurações (settings)

| Variável | Padrão | Descrição |
|---|---|---|
| `DEEPSEEK_API_KEY` | vazio | Chave da API DeepSeek, lida do ambiente |
| `DEEPSEEK_MODEL` | `deepseek-chat` | Identificador do modelo (V3/V4 conforme a versão contratada) |
| `AI_ANALYSIS_ENABLED` | `True` | Feature flag; desligada automaticamente se não houver chave |
| `AI_ANALYSIS_MIN_INTERVAL_MINUTES` | `15` | Intervalo mínimo entre gerações sob demanda por usuário |
| `AI_AGENT_TIMEOUT_SECONDS` | `60` | Timeout de uma execução do agente |
| `AI_AGENT_MAX_ITERATIONS` | `10` | Teto de iterações do loop do agente |
| `AI_ANALYSIS_MONTHS_WINDOW` | `6` | Janela padrão de meses considerada na análise |

#### 8.5.6 Decisões de arquitetura

- **Execução síncrona no MVP.** A geração sob demanda ocorre dentro do request (POST), com estado de carregamento na interface. Fila assíncrona (Celery/RQ) fica como evolução futura — adotá-la agora violaria o RNF07 (simplicidade).
- **Sem SQL livre.** Nenhum toolkit de SQL genérico é usado. Toda leitura passa por tools com queries fixas no ORM, o que elimina a classe de risco de um modelo consultar dados de outro usuário.
- **A app `ai` não altera dados.** O agente apenas lê o domínio financeiro; a única escrita é a própria `AIAnalysis`.
- **Documentação viva.** A API do LangChain 1.0 deve ser confirmada via MCP context7 durante a implementação (RNF16); nomes de funções não devem ser assumidos de memória.

---

## 9. Design System

### 9.1 Paleta de Cores (TailwindCSS classes)

| Papel | Classe TailwindCSS | Hex aproximado | Uso |
|---|---|---|---|
| **Background principal** | `bg-gray-950` | #0B0F19 | Fundo do body |
| **Background cards** | `bg-gray-900` | #111827 | Cards, sidebar, modals |
| **Background inputs** | `bg-gray-800` | #1F2937 | Campos de formulário |
| **Border padrão** | `border-gray-700` | #374151 | Bordas de cards, inputs, dividers |
| **Texto primário** | `text-gray-100` | #F3F4F6 | Títulos, texto principal |
| **Texto secundário** | `text-gray-400` | #9CA3AF | Labels, descrições, placeholders |
| **Accent primário** | `bg-emerald-500` | #10B981 | Botões primários, entradas |
| **Accent hover** | `hover:bg-emerald-600` | #059669 | Hover de botões primários |
| **Accent secundário** | `bg-violet-500` | #8B5CF6 | Destaques, badges, links ativos |
| **Perigo / Saída** | `bg-rose-500` | #F43F5E | Botão excluir, valores de saída |
| **Sucesso** | `text-emerald-400` | #34D399 | Valores de entrada, saldo positivo |
| **Alerta** | `text-amber-400` | #FBBF24 | Avisos, saldo baixo |
| **Gradient header** | `bg-gradient-to-r from-emerald-500 to-violet-500` | — | Barra superior, títulos especiais |

### 9.2 Tipografia

| Elemento | Classes TailwindCSS |
|---|---|
| **Font família** | `font-sans` (Inter via Google Fonts como fallback do sistema) |
| **Título da página (h1)** | `text-2xl font-bold text-gray-100` |
| **Subtítulo (h2)** | `text-xl font-semibold text-gray-100` |
| **Título de card (h3)** | `text-lg font-semibold text-gray-100` |
| **Corpo de texto** | `text-sm text-gray-300` |
| **Label** | `text-sm font-medium text-gray-400` |
| **Texto auxiliar** | `text-xs text-gray-500` |

### 9.3 Botões

```html
<!-- Primário -->
<button class="bg-emerald-500 hover:bg-emerald-600 text-white font-medium
    py-2 px-4 rounded-lg transition-colors duration-200">
    Salvar
</button>

<!-- Secundário -->
<button class="bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium
    py-2 px-4 rounded-lg transition-colors duration-200">
    Cancelar
</button>

<!-- Perigo -->
<button class="bg-rose-500 hover:bg-rose-600 text-white font-medium
    py-2 px-4 rounded-lg transition-colors duration-200">
    Excluir
</button>

<!-- Outline -->
<button class="border border-gray-600 hover:border-emerald-500
    text-gray-300 hover:text-emerald-400 font-medium
    py-2 px-4 rounded-lg transition-colors duration-200">
    Ver detalhes
</button>
```

### 9.4 Inputs e Formulários

```html
<!-- Campo de texto -->
<div class="mb-4">
    <label class="block text-sm font-medium text-gray-400 mb-1">E-mail</label>
    <input type="email"
        class="w-full bg-gray-800 border border-gray-700 rounded-lg
        py-2 px-3 text-gray-100 placeholder-gray-500
        focus:outline-none focus:ring-2 focus:ring-emerald-500
        focus:border-emerald-500 transition-colors duration-200"
        placeholder="seu@email.com">
</div>

<!-- Select -->
<select class="w-full bg-gray-800 border border-gray-700 rounded-lg
    py-2 px-3 text-gray-100 focus:outline-none focus:ring-2
    focus:ring-emerald-500 focus:border-emerald-500
    transition-colors duration-200">
    <option value="">Selecione...</option>
</select>

<!-- Form container -->
<form class="bg-gray-900 border border-gray-700 rounded-xl p-6 space-y-4">
    <!-- campos aqui -->
</form>
```

### 9.5 Cards

```html
<!-- Card padrão -->
<div class="bg-gray-900 border border-gray-700 rounded-xl p-6">
    <h3 class="text-lg font-semibold text-gray-100 mb-2">Título</h3>
    <p class="text-sm text-gray-400">Conteúdo do card</p>
</div>

<!-- Card com destaque (gradient top border) -->
<div class="bg-gray-900 border border-gray-700 rounded-xl p-6
    border-t-2 border-t-emerald-500">
    <h3 class="text-lg font-semibold text-gray-100 mb-2">Saldo Total</h3>
    <p class="text-3xl font-bold text-emerald-400">R$ 5.230,00</p>
</div>
```

### 9.6 Layout e Grid

```html
<!-- Container principal (logado) -->
<div class="min-h-screen bg-gray-950 text-gray-100">
    <!-- Navbar fixa no topo -->
    <nav class="bg-gray-900 border-b border-gray-700 px-6 py-3">
        <!-- logo, menu, user info -->
    </nav>

    <div class="flex">
        <!-- Sidebar (desktop) -->
        <aside class="hidden md:block w-64 bg-gray-900 border-r
            border-gray-700 min-h-screen p-4">
            <!-- links de navegação -->
        </aside>

        <!-- Conteúdo principal -->
        <main class="flex-1 p-6">
            <!-- conteúdo da página -->
        </main>
    </div>
</div>

<!-- Grid responsivo para cards do dashboard -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- cards -->
</div>

<!-- Grid de tabela responsiva -->
<div class="overflow-x-auto">
    <table class="w-full text-sm text-left">
        <thead class="text-xs text-gray-400 uppercase bg-gray-800">
            <tr>
                <th class="px-4 py-3">Coluna</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
            <tr class="bg-gray-900 hover:bg-gray-800 transition-colors">
                <td class="px-4 py-3 text-gray-300">Valor</td>
            </tr>
        </tbody>
    </table>
</div>
```

### 9.7 Navbar e Sidebar

```html
<!-- Navbar -->
<nav class="bg-gray-900/80 backdrop-blur-sm border-b border-gray-700
    px-6 py-3 flex items-center justify-between sticky top-0 z-50">
    <!-- Logo com gradient -->
    <a href="/" class="text-xl font-bold bg-gradient-to-r
        from-emerald-400 to-violet-400 bg-clip-text text-transparent">
        Finanpy
    </a>
    <!-- User menu -->
    <div class="flex items-center gap-4">
        <span class="text-sm text-gray-400">Olá, {{ user.first_name }}</span>
        <a href="{% url 'logout' %}" class="text-sm text-gray-400 hover:text-rose-400
            transition-colors">Sair</a>
    </div>
</nav>

<!-- Sidebar item -->
<a href="#" class="flex items-center gap-3 px-3 py-2 rounded-lg
    text-gray-400 hover:text-gray-100 hover:bg-gray-800
    transition-colors duration-200">
    <!-- ícone SVG -->
    <span class="text-sm font-medium">Dashboard</span>
</a>

<!-- Sidebar item ativo -->
<a href="#" class="flex items-center gap-3 px-3 py-2 rounded-lg
    text-emerald-400 bg-emerald-500/10">
    <!-- ícone SVG -->
    <span class="text-sm font-medium">Dashboard</span>
</a>
```

### 9.8 Mensagens de Feedback (Django Messages)

```html
<!-- Sucesso -->
<div class="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400
    rounded-lg px-4 py-3 text-sm">
    Operação realizada com sucesso!
</div>

<!-- Erro -->
<div class="bg-rose-500/10 border border-rose-500/30 text-rose-400
    rounded-lg px-4 py-3 text-sm">
    Erro ao processar sua solicitação.
</div>

<!-- Alerta -->
<div class="bg-amber-500/10 border border-amber-500/30 text-amber-400
    rounded-lg px-4 py-3 text-sm">
    Atenção: verifique os campos destacados.
</div>
```

### 9.9 Modal de Confirmação

```html
<!-- Overlay + Modal -->
<div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center
    justify-center z-50">
    <div class="bg-gray-900 border border-gray-700 rounded-xl p-6
        w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold text-gray-100 mb-2">
            Confirmar exclusão
        </h3>
        <p class="text-sm text-gray-400 mb-6">
            Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.
        </p>
        <div class="flex justify-end gap-3">
            <button class="bg-gray-700 hover:bg-gray-600 text-gray-200
                font-medium py-2 px-4 rounded-lg">Cancelar</button>
            <button class="bg-rose-500 hover:bg-rose-600 text-white
                font-medium py-2 px-4 rounded-lg">Excluir</button>
        </div>
    </div>
</div>
```

### 9.10 Card de Análise de IA (dashboard)

O card usa o accent secundário (violet) para se diferenciar dos cards financeiros, que usam emerald/rose.

```html
<!-- Card da última análise de IA -->
<div class="bg-gray-900 border border-gray-700 rounded-xl p-6
    border-t-2 border-t-violet-500">
    <div class="flex items-start justify-between mb-4">
        <div class="flex items-center gap-2">
            <!-- ícone sparkles SVG -->
            <h3 class="text-lg font-semibold text-gray-100">Análise Inteligente</h3>
        </div>
        <span class="text-xs text-gray-500">Gerada em 02/08/2026 às 14:32</span>
    </div>

    <!-- Indicador de saúde financeira -->
    <div class="flex items-center gap-3 mb-4">
        <span class="text-3xl font-bold text-emerald-400">78</span>
        <span class="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400
            text-xs font-medium px-2 py-1 rounded-full">Boa</span>
    </div>

    <p class="text-sm text-gray-300 mb-4">Resumo do diagnóstico do período...</p>

    <h4 class="text-sm font-medium text-gray-400 mb-2">Insights</h4>
    <ul class="space-y-1 mb-4 text-sm text-gray-300 list-disc list-inside">
        <li>Alimentação consumiu 38% das saídas do mês.</li>
    </ul>

    <h4 class="text-sm font-medium text-gray-400 mb-2">Dicas</h4>
    <ul class="space-y-1 mb-4 text-sm text-gray-300 list-disc list-inside">
        <li>Estabeleça um teto de R$ 800 para Alimentação.</li>
    </ul>

    <div class="flex items-center justify-between pt-4 border-t border-gray-700">
        <a href="{% url 'ai:analysis_list' %}"
            class="text-sm text-violet-400 hover:text-violet-300 transition-colors">
            Ver histórico
        </a>
        <form method="post" action="{% url 'ai:generate' %}">
            {% csrf_token %}
            <button type="submit" class="bg-violet-500 hover:bg-violet-600 text-white
                font-medium py-2 px-4 rounded-lg transition-colors duration-200">
                Gerar nova análise
            </button>
        </form>
    </div>
</div>

<!-- Estado vazio -->
<div class="bg-gray-900 border border-dashed border-gray-700 rounded-xl p-6 text-center">
    <p class="text-sm text-gray-400 mb-4">
        Você ainda não tem uma análise. Gere a primeira e receba insights sobre suas finanças.
    </p>
    <!-- botão "Gerar análise" -->
</div>
```

**Cores do indicador de saúde:**

| Rótulo | Faixa | Classe |
|---|---|---|
| Crítica | 0–39 | `text-rose-400` / `bg-rose-500/10` |
| Atenção | 40–59 | `text-amber-400` / `bg-amber-500/10` |
| Boa | 60–84 | `text-emerald-400` / `bg-emerald-500/10` |
| Excelente | 85–100 | `text-violet-400` / `bg-violet-500/10` |

---

## 10. User Stories

### Épico 1 — Autenticação e Perfil

**US01 — Cadastro de usuário**
> Como visitante, quero me cadastrar com nome, e-mail e senha para ter acesso ao sistema.

Critérios de aceite:
- Formulário exige nome, e-mail, senha e confirmação de senha.
- E-mail deve ser único; exibir erro se já cadastrado.
- Senha com mínimo de 8 caracteres (validação nativa Django).
- Após cadastro, o usuário é logado automaticamente e redirecionado ao dashboard.

**US02 — Login via e-mail**
> Como usuário cadastrado, quero fazer login com meu e-mail e senha para acessar o sistema.

Critérios de aceite:
- Campo de login é **e-mail** (não username).
- Mensagem de erro genérica em caso de credenciais inválidas.
- Após login, redireciona ao dashboard.

**US03 — Logout**
> Como usuário logado, quero fazer logout para encerrar minha sessão.

Critérios de aceite:
- Botão de logout visível no menu/navbar.
- Após logout, redireciona à landing page.

**US04 — Edição de perfil**
> Como usuário logado, quero editar meu nome e e-mail.

Critérios de aceite:
- Formulário pré-preenchido com dados atuais.
- Validação de e-mail único ao alterar.
- Mensagem de sucesso após salvar.

### Épico 2 — Contas Bancárias

**US05 — Criar conta bancária**
> Como usuário logado, quero criar uma conta bancária para registrar meu saldo.

Critérios de aceite:
- Campos: nome, tipo (Corrente, Poupança, Carteira, Investimento), saldo inicial.
- Saldo atual é definido como saldo inicial na criação.
- Conta vinculada ao usuário logado.

**US06 — Listar contas bancárias**
> Como usuário logado, quero ver todas as minhas contas bancárias e seus saldos.

Critérios de aceite:
- Lista apenas contas do usuário logado.
- Exibe nome, tipo e saldo atual de cada conta.
- Botões de editar e excluir por conta.

**US07 — Editar conta bancária**
> Como usuário logado, quero editar nome e tipo da minha conta.

Critérios de aceite:
- Formulário pré-preenchido.
- Não permite editar saldo inicial (é histórico).
- Mensagem de sucesso.

**US08 — Excluir conta bancária**
> Como usuário logado, quero excluir uma conta que não uso mais.

Critérios de aceite:
- Modal de confirmação antes de excluir.
- Exclui todas as transações vinculadas (CASCADE) ou impede exclusão se houver transações (definir na sprint).
- Mensagem de sucesso.

### Épico 3 — Categorias

**US09 — Criar categoria**
> Como usuário logado, quero criar categorias para organizar minhas transações.

Critérios de aceite:
- Campos: nome e tipo (Entrada ou Saída).
- Categoria vinculada ao usuário logado.

**US10 — Listar categorias**
> Como usuário logado, quero ver todas as minhas categorias.

Critérios de aceite:
- Lista separada ou filtrada por tipo (entrada/saída).
- Botões de editar e excluir.

**US11 — Editar categoria**
> Como usuário logado, quero editar o nome e tipo de uma categoria.

Critérios de aceite:
- Formulário pré-preenchido.
- Mensagem de sucesso.

**US12 — Excluir categoria**
> Como usuário logado, quero excluir uma categoria que não uso mais.

Critérios de aceite:
- Modal de confirmação.
- Impede exclusão se houver transações vinculadas (exibe mensagem).

**US13 — Categorias padrão no cadastro**
> Como novo usuário, quero ter categorias pré-cadastradas para começar a usar rápido.

Critérios de aceite:
- Ao criar conta, gerar automaticamente: Salário, Freelance (entrada); Alimentação, Transporte, Moradia, Lazer, Saúde, Educação (saída).
- Implementado via signal `post_save` no model User.

### Épico 4 — Transações

**US14 — Criar transação**
> Como usuário logado, quero registrar uma transação de entrada ou saída.

Critérios de aceite:
- Campos: descrição, valor, data, tipo (entrada/saída), conta, categoria.
- Categorias filtradas pelo tipo selecionado.
- Ao salvar, o saldo da conta é atualizado (+ para entrada, - para saída).

**US15 — Listar transações**
> Como usuário logado, quero ver todas as minhas transações.

Critérios de aceite:
- Listagem paginada (20 por página).
- Filtros: período (data inicial/final), tipo, conta, categoria.
- Exibe: data, descrição, categoria, conta, valor (verde entrada, vermelho saída).

**US16 — Editar transação**
> Como usuário logado, quero editar uma transação existente.

Critérios de aceite:
- Formulário pré-preenchido.
- Ao salvar, recalcular saldo da conta (reverter valor antigo, aplicar novo).

**US17 — Excluir transação**
> Como usuário logado, quero excluir uma transação errada.

Critérios de aceite:
- Modal de confirmação.
- Ao excluir, reverter o efeito no saldo da conta.

### Épico 5 — Dashboard

**US18 — Visualizar dashboard**
> Como usuário logado, quero ver um resumo da minha situação financeira ao entrar no sistema.

Critérios de aceite:
- Card com saldo total (soma de todas as contas).
- Card com total de entradas do mês corrente.
- Card com total de saídas do mês corrente.
- Card com balanço do mês (entradas - saídas).
- Lista das 5 últimas transações.
- Resumo de gastos por categoria (mês corrente).

### Épico 6 — Landing Page

**US19 — Página de apresentação**
> Como visitante, quero ver uma página bonita que explique o sistema e me permita cadastrar ou entrar.

Critérios de aceite:
- Hero section com título, descrição e CTA para cadastro.
- Seção de funcionalidades.
- Botões "Cadastre-se" e "Entrar" visíveis.
- Se já logado, redireciona ao dashboard.

### Épico 7 — Agente de IA

**US20 — Ver a última análise no dashboard**
> Como usuário logado, quero ver no dashboard a análise mais recente das minhas finanças, com insights e dicas, para entender minha situação sem precisar interpretar os números sozinho.

Critérios de aceite:
- O card exibe resumo, insights, dicas, indicador de saúde e data de geração da **última análise bem-sucedida** do usuário logado.
- Se o usuário nunca gerou uma análise, o card mostra o estado vazio com chamada para gerar a primeira.
- O card nunca exibe análise de outro usuário.
- Se a funcionalidade estiver desligada (`AI_ANALYSIS_ENABLED=False`), o card não aparece e o restante do dashboard segue normal.

**US21 — Gerar uma nova análise sob demanda**
> Como usuário logado, quero solicitar uma nova análise para atualizar o diagnóstico depois de registrar transações novas.

Critérios de aceite:
- Botão "Gerar nova análise" no card do dashboard, via POST com `{% csrf_token %}`.
- Enquanto processa, a interface indica carregamento e impede duplo envio.
- Ao concluir, redireciona ao dashboard com mensagem de sucesso e o card já atualizado.
- Se a última geração foi há menos de `AI_ANALYSIS_MIN_INTERVAL_MINUTES`, exibe mensagem de alerta informando quando será possível gerar de novo.
- Em caso de falha na API, exibe mensagem de erro amigável e o dashboard continua utilizável.

**US22 — Consultar o histórico de análises**
> Como usuário logado, quero ver as análises anteriores para acompanhar a evolução das minhas finanças ao longo do tempo.

Critérios de aceite:
- Página `/analises/` lista as análises do usuário logado em ordem decrescente de data, com paginação.
- Cada item mostra data, indicador de saúde e trecho do resumo.
- Detalhe individual exibe a análise completa.
- Acesso ao detalhe de uma análise de outro usuário retorna 404.

**US23 — Gerar análises para todos os usuários (operação)**
> Como responsável pelo sistema, quero rodar um comando que gera a análise de todos os usuários, para manter o dashboard de cada um atualizado.

Critérios de aceite:
- `python manage.py run_ai_analysis` percorre todos os usuários ativos e gera uma análise por usuário, usando apenas os dados de cada um.
- Opção `--user <email>` para gerar de um único usuário.
- Falha em um usuário não interrompe a execução dos demais; erros são registrados.
- Ao final, o comando reporta o total de sucessos e falhas.

**US24 — Análise honesta com poucos dados**
> Como usuário novo, quero que a análise diga que ainda não há dados suficientes em vez de inventar conclusões.

Critérios de aceite:
- Com nenhuma ou pouquíssimas transações, a análise declara a limitação explicitamente.
- O agente não apresenta números que não vieram das tools.

---

## 11. Métricas de Sucesso

### KPIs de Produto

| Métrica | Descrição | Meta |
|---|---|---|
| Funcionalidades entregues | CRUDs + dashboard completos e funcionais | 100% dos RF |
| Bugs críticos | Bugs que impedem uso em produção | 0 |
| Consistência visual | Todas as telas seguem o Design System | 100% |

### KPIs de Usuário

| Métrica | Descrição | Meta |
|---|---|---|
| Cadastro → Dashboard | Usuário consegue cadastrar e chegar ao dashboard | < 60s |
| Tempo para criar transação | Do clique em "Nova transação" ao salvamento | < 30s |
| Compreensão da interface | Usuário realiza tarefas sem instrução | > 90% das tarefas |

### KPIs Técnicos

| Métrica | Descrição | Meta |
|---|---|---|
| Tempo de carregamento | Páginas autenticadas | < 2s |
| Cobertura de código | (para sprints finais) | > 80% |
| Conformidade PEP08 | Código passa em linters | 100% |

### KPIs do Agente de IA

| Métrica | Descrição | Meta |
|---|---|---|
| Taxa de sucesso da análise | Execuções com `status='success'` sobre o total | > 95% |
| Tempo de geração | Duração de uma execução do agente | < 60s |
| Vazamento entre usuários | Análises contendo dados de outro usuário | 0 (bloqueante) |
| Fidelidade aos dados | Números citados na análise conferem com o banco | 100% em amostragem |
| Custo por análise | Tokens consumidos por execução | Monitorado via `total_tokens` |

---

## 12. Riscos e Mitigações

| # | Risco | Impacto | Probabilidade | Mitigação |
|---|---|---|---|---|
| R1 | TailwindCSS via CDN causa lentidão | Médio | Baixa | Migrar para TailwindCSS standalone CLI se necessário |
| R2 | SQLite não suporta concorrência | Baixo | Baixa | Sistema é mono-usuário local; migrar para PostgreSQL se escalar |
| R3 | Perda de dados sem backup | Alto | Média | Documentar rotina de backup do db.sqlite3 |
| R4 | Complexidade crescente sem testes | Alto | Alta | Sprints finais dedicados a testes automatizados |
| R5 | Login por e-mail conflita com libs de terceiros | Médio | Baixa | Usar `AbstractUser` com `USERNAME_FIELD = 'email'` desde o início |
| R6 | Inconsistência de saldos | Alto | Média | Centralizar lógica de atualização de saldo em método do model ou signal |
| R7 | Scope creep (adição de features fora do escopo) | Médio | Alta | Seguir estritamente o PRD; não implementar o que não for solicitado |
| R8 | **Vazamento de dados entre usuários pelo agente** | Crítico | Média | `user_id` fixado no servidor por closure nas tools; proibição de SQL livre; teste automatizado dedicado ao isolamento |
| R9 | **Alucinação de números pelo modelo** | Alto | Alta | Prompt exige usar somente valores retornados pelas tools; saída estruturada validada por Pydantic; instrução explícita para declarar falta de dados |
| R10 | **Indisponibilidade ou custo da API DeepSeek** | Médio | Média | Feature flag, timeout, teto de iterações, intervalo mínimo entre gerações; falha isolada em try/except sem quebrar o dashboard |
| R11 | **Vazamento da chave de API** | Alto | Média | `DEEPSEEK_API_KEY` só em variável de ambiente/`.env`; `.env` já ignorado no git; nunca logar a chave |
| R12 | **Requisição longa travando o worker** | Médio | Média | Timeout por execução; geração em lote via management command fora do ciclo de request; fila assíncrona como evolução |
| R13 | **API do LangChain 1.0 assumida de memória** | Médio | Alta | Implementação obrigada a consultar a documentação vigente via MCP context7 (RNF16) |


> **Nota final:** Este PRD é um documento vivo. Deve ser atualizado conforme decisões evoluam durante as sprints. Priorizar entregas incrementais e evitar adicionar funcionalidades fora do escopo definido.