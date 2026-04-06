---
name: URL Namespace Bug Pattern
description: Templates that referenced URL names without namespace caused 500 errors on all authenticated pages
type: project
---

## Bug discovered during T15.3 (2026-04-05)

All authenticated pages (dashboard, contas, categorias, transacoes, perfil) returned HTTP 500 due to `NoReverseMatch: Reverse for 'logout' not found` in `templates/components/navbar.html`.

**Root cause:** `users/urls.py` has `app_name = 'users'`, so all URLs are namespaced. Templates were using `{% url 'logout' %}` instead of `{% url 'users:logout' %}`.

**Files fixed:**
- `templates/components/navbar.html`: `'logout'` → `'users:logout'`
- `templates/landing.html`: `'login'` → `'users:login'`, `'signup'` → `'users:signup'` (4 occurrences)

**Note:** `templates/users/login.html` and `templates/users/signup.html` already use the correct `users:` namespace.

**How to apply:** When adding new URL references in templates, always check whether the target app has `app_name` set in its `urls.py`. If yes, use `appname:urlname` format.
