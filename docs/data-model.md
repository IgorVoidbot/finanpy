# Modelo de Dados

## Diagrama ER

```
USER ||--|| PROFILE : "tem"
USER ||--o{ ACCOUNT : "possui"
USER ||--o{ CATEGORY : "cria"
USER ||--o{ TRANSACTION : "registra"
ACCOUNT ||--o{ TRANSACTION : "pertence"
CATEGORY ||--o{ TRANSACTION : "classifica"
```

## Entidades

### User
Herda de `AbstractUser`. Login feito via e-mail (não username).

| Campo | Tipo | Detalhe |
|---|---|---|
| `email` | EmailField | unique, `USERNAME_FIELD` |
| `first_name` | CharField | — |
| `last_name` | CharField | — |
| `password` | CharField | hash nativo Django |
| `is_active` | BooleanField | — |
| `date_joined` | DateTimeField | — |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

### Profile
Criado automaticamente via signal `post_save` ao registrar um User.

| Campo | Tipo | Detalhe |
|---|---|---|
| `user` | OneToOneField | → User |
| `display_name` | CharField | max 100 |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

### Account

| Campo | Tipo | Detalhe |
|---|---|---|
| `user` | ForeignKey | → User |
| `name` | CharField | max 100 |
| `account_type` | CharField | choices: `checking`, `savings`, `wallet`, `investment` |
| `initial_balance` | DecimalField | 10,2 — default 0 |
| `current_balance` | DecimalField | 10,2 — atualizado conforme transações |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

### Category
Categorias padrão criadas automaticamente via signal `post_save` ao registrar um User.

| Campo | Tipo | Detalhe |
|---|---|---|
| `user` | ForeignKey | → User |
| `name` | CharField | max 50 |
| `transaction_type` | CharField | choices: `income`, `expense` |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

Restrição: `unique_together = [user, name, transaction_type]`

**Categorias padrão criadas no cadastro:**
- Entrada: Salário, Freelance
- Saída: Alimentação, Transporte, Moradia, Lazer, Saúde, Educação

### Transaction

| Campo | Tipo | Detalhe |
|---|---|---|
| `user` | ForeignKey | → User |
| `account` | ForeignKey | → Account |
| `category` | ForeignKey | → Category |
| `description` | CharField | max 200 |
| `amount` | DecimalField | 10,2 |
| `transaction_type` | CharField | choices: `income`, `expense` |
| `date` | DateField | — |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

Ordering padrão: `-date`, `-created_at`

Ao criar, editar ou excluir uma transação, `current_balance` da Account associada é recalculado.
