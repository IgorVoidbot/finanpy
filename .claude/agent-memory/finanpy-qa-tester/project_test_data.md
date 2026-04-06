---
name: Finanpy Test Data and Credentials
description: Known working test credentials and user data created during QA sessions
type: project
---

## Superuser credentials (admin access)
- Email: igordanilo@gmail.com
- Password: 123456789
- Access: http://127.0.0.1:8000/admin/

## Test user created during T2.5 (2026-04-05)
- Email: teste@finanpy.com
- First name: Teste
- Last name: Finanpy
- Password: TesteSenha123
- User ID in DB: 2
- is_active: True
- Profile: created manually via Django shell during T15.3 (was missing — post_save signal had not run for this user)

**Why:** Created during test T2.5 to verify Django Admin user creation flow with custom User model.
**How to apply:** Use these credentials in future authenticated test flows. Do not recreate if already in DB — check first or use a different email suffix. If `/perfil/` gives RelatedObjectDoesNotExist, run `Profile.objects.create(user=user)` in the shell.

## QA test user created during T16.3 (2026-04-05)
- Email: test@test.com
- Password: testpass123
- First name: QA / Last name: Tester
- Created via `User.objects.create_user()` in shell — did not pre-exist in DB

**Why:** T16.3 spec listed test@test.com but the user did not exist; must be created before Playwright tests.
**How to apply:** Always verify `test@test.com` exists before running browser tests. If missing, create via shell. Default categories are auto-created by post_save signal.

## QA test data naming convention (T16.3)
- Accounts: `Conta QA Para Excluir`, `Conta QA Permanente`
- Categories: `Categoria QA Para Excluir`, `Categoria QA Para Excluir 2`
- Transactions: `Transacao QA Para Excluir`, `Transacao QA Para Excluir 2`

Cleanup command:
```python
u = User.objects.get(email='test@test.com')
Category.objects.filter(user=u, name__contains='QA').delete()
Account.objects.filter(user=u, name__contains='QA').delete()
Transaction.objects.filter(user=u, description__contains='QA').delete()
```
