---
name: Finanpy Template Structure
description: Template hierarchy, block names, URL names referenced, and component locations established in the initial template build
type: project
---

Templates live in `templates/` at the project root. Hierarchy:

- `base.html` — raw base: Tailwind CDN, Inter font, `{% block content %}`, `{% block extra_js %}`
- `base_auth.html` — extends base.html; blocks: `{% block auth_title %}`, `{% block auth_content %}`; centered card layout, no sidebar
- `base_app.html` — extends base.html; blocks: `{% block app_title %}`, `{% block page_content %}`; includes navbar + sidebar + messages
- `landing.html` — extends base.html directly; standalone public page with JS redirect if `user.is_authenticated`

Components (included via `{% include %}`):
- `components/navbar.html` — sticky top bar, hamburger button id="menu-toggle", uses `{% url 'dashboard' %}` and `{% url 'logout' %}`
- `components/sidebar.html` — hidden on mobile; active detection via `request.resolver_match.app_name` and `url_name`; uses `{% url ... as var %}{% if var %}` pattern to avoid NoReverseMatch
- `components/messages.html` — Django messages with JS auto-dismiss at 5000ms and manual X button; uses `data-message` attribute

URL names referenced across templates (must exist in urls.py before templates work):
- `dashboard` (root, no namespace)
- `landing` (root, no namespace)
- `login`, `logout`, `signup` (root, no namespace — likely from users app)
- `accounts:list` (namespace: accounts)
- `categories:list` (namespace: categories)
- `transactions:list` (namespace: transactions)
- `profiles:edit` (namespace: profiles)

Active sidebar detection pattern:
- Dashboard: `request.resolver_match.url_name == 'dashboard'`
- Other apps: `request.resolver_match.app_name == '<app_name>'`

**Why:** None of the apps had urls.py yet at template creation time — the `{% url ... as var %}{% if var %}` pattern prevents NoReverseMatch errors while URLs are progressively wired up.

**How to apply:** When adding new sidebar links or navbar links, always use the silent `{% url ... as var %}` pattern until the corresponding url is confirmed registered.
