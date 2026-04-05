# Setup

## Pré-requisitos

- Python 3.13+
- pip

## Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd pyfinance

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Banco de dados

```bash
python manage.py migrate
```

## Rodando o servidor

```bash
python manage.py runserver
```

O servidor estará disponível em `http://127.0.0.1:8000`.

## Dependências

| Pacote | Versão |
|--------|--------|
| Django | 6.0.3 |
| asgiref | 3.11.1 |
| sqlparse | 0.5.5 |
| tzdata | 2026.1 |

## Configurações relevantes (`core/settings.py`)

| Configuração | Valor atual |
|---|---|
| `DEBUG` | `True` |
| `DATABASE` | SQLite (`db.sqlite3`) |
| `LANGUAGE_CODE` | `en-us` |
| `TIME_ZONE` | `UTC` |
| `STATIC_URL` | `static/` |

> `SECRET_KEY` está hardcoded apenas para desenvolvimento. Em produção, use variável de ambiente.
