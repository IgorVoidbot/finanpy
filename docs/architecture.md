# Arquitetura

## Stack

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.13+ |
| Framework | Django 6.0.3 |
| Frontend | Django Template Language |
| Estilização | TailwindCSS (via CDN) |
| Banco de dados | SQLite3 |
| Autenticação | `django.contrib.auth` (login via e-mail) |
| Gerenciamento de pacotes | pip + `requirements.txt` |

## Estrutura de Apps

Cada domínio do sistema vive em sua própria Django app:

| App | Responsabilidade |
|---|---|
| `core/` | Configurações globais do projeto (settings, urls, wsgi, asgi) |
| `users/` | Model de usuário customizado e autenticação |
| `profiles/` | Perfil do usuário |
| `accounts/` | Contas bancárias |
| `categories/` | Categorias de transações |
| `transactions/` | Transações financeiras |

## Estrutura de Diretórios

```
pyfinance/
├── core/               # Configurações globais
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/
├── profiles/
├── accounts/
├── categories/
├── transactions/
├── templates/          # Templates globais (base, components, landing, dashboard)
│   ├── base.html
│   ├── landing.html
│   ├── dashboard.html
│   └── components/
│       ├── navbar.html
│       ├── sidebar.html
│       ├── card.html
│       ├── modal_confirm.html
│       └── messages.html
├── static/             # Arquivos estáticos globais
│   ├── css/
│   └── js/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

> `templates/` e `static/` ainda não existem — serão criados durante o desenvolvimento.

## Convenções de Código

### Geral

- **Idioma do código:** inglês (variáveis, funções, classes, comentários)
- **Idioma da interface:** português brasileiro
- **Estilo:** PEP 8, aspas simples
- **Views:** class-based views (CBVs) sempre que possível
- **Sem over-engineering:** usar recursos nativos do Django; evitar abstrações desnecessárias

### Models

- Todos os models devem ter `created_at` (`auto_now_add=True`) e `updated_at` (`auto_now=True`)
- Campos DecimalField para valores monetários: `max_digits=10`, `decimal_places=2`
- Isolamento por usuário: toda entidade deve ter FK para `User` e filtrar por `request.user` nas views

### Segurança

- Proteção CSRF habilitada (middleware padrão do Django)
- Senhas com hash (autenticação nativa do Django)
- Todo acesso às views autenticadas restrito por `LoginRequiredMixin`
