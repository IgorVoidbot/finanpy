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

**Why:** Created during test T2.5 to verify Django Admin user creation flow with custom User model.
**How to apply:** Use these credentials in future authenticated test flows. Do not recreate if already in DB — check first or use a different email suffix.
