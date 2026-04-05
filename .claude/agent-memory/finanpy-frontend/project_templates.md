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

Profile edit template:
- `templates/profiles/profile_edit.html` — extends `base_app.html`; two forms in one `<form method="post">`: `user_form` (first_name, last_name, email) and `profile_form` (display_name); first/last name in 2-column grid `grid grid-cols-1 sm:grid-cols-2`; each section separated by a `border-b border-gray-700` heading; submit button right-aligned above a `border-t border-gray-700` divider; all fields rendered manually for full Tailwind control

Auth child templates (T4.4 and T4.6):
- `templates/users/signup.html` — extends `base_auth.html`; fields: `form.first_name`, `form.last_name`, `form.email`, `form.password1`, `form.password2`; links to `users:login`
- `templates/users/login.html` — extends `base_auth.html`; fields: `form.username` (email), `form.password`; links to `users:signup`
- Both render non-field errors above the form with rose styling; per-field errors below each input in rose; no JS required
- Input fields rendered manually (not `{{ form.as_p }}`) for full Tailwind styling control using `form.field.html_name`, `form.field.id_for_label`, `form.field.value`
- First/last name fields use a 2-column grid: `grid grid-cols-1 gap-4 sm:grid-cols-2`

URL names referenced across templates (must exist in urls.py before templates work):
- `dashboard` (root, no namespace)
- `landing` (root, no namespace)
- `login`, `logout`, `signup` (root, no namespace — likely from users app)
- `users:login`, `users:signup` (namespace: users — used in auth templates)
- `accounts:account_list`, `accounts:account_create`, `accounts:account_update`, `accounts:account_delete` (namespace: accounts)
- `categories:category_list`, `categories:category_create`, `categories:category_update`, `categories:category_delete` (namespace: categories)
- `transactions:transaction_list`, `transactions:transaction_create`, `transactions:transaction_update`, `transactions:transaction_delete` (namespace: transactions)
- `profiles:edit` (namespace: profiles)

Categories templates (T10.3, T10.5, T10.8):
- `templates/categories/category_list.html` — table with `overflow-x-auto`, transaction_type badge uses `{% if category.transaction_type == 'income' %}` to pick `bg-emerald-500/20 text-emerald-400` vs `bg-rose-500/20 text-rose-400`; `get_transaction_type_display` for label text; empty state with tag SVG icon; colspan="3"
- `templates/categories/category_form.html` — shared create/edit form; `<select>` iterates `form.transaction_type.field.choices` skipping empty option with `{% if value %}`; no field gated behind `{% if object %}` (both create and edit use name + transaction_type)
- `templates/categories/category_confirm_delete.html` — centered `max-w-lg mx-auto` card with rose warning icon SVG; shows `{{ object.name }}` and inline type badge (`get_transaction_type_display`) with emerald/rose coloring

Accounts templates (T7.3, T7.5, T7.8):
- `templates/accounts/account_list.html` — table with responsive overflow-x-auto, `get_account_type_display` for type badge, conditional emerald/rose coloring on `current_balance` via `>= 0` check, empty state with SVG bank icon
- `templates/accounts/account_form.html` — shared create/edit form; `{% if object %}` gates the `initial_balance` field (hidden on edit); `<select>` iterates `form.account_type.field.choices` with `{% for value, label in ... %}`; selected option uses `form.account_type.value == value`
- `templates/accounts/account_confirm_delete.html` — centered `max-w-lg mx-auto` card with rose warning icon SVG, `{{ object.name }}` in bold, standard POST form

Transactions templates (T13.4, T13.6, T13.9):
- `templates/transactions/transaction_list.html` — filter bar in 5-column responsive grid (date_from, date_to, transaction_type, account, category); filter `selected` state uses `|stringformat:'s'` comparison for FK pk values; pagination preserves filter params by repeating `{% if filters.X %}&X={{ filters.X }}{% endif %}` on each page link; edit action uses violet icon SVG, delete uses rose icon SVG; empty-state colspan="7"
- `templates/transactions/transaction_form.html` — amount+date in `sm:grid-cols-2` grid; account+category in second `sm:grid-cols-2` grid; ModelChoiceField selects (account, category) use `|stringformat:'s'` on both sides of selected comparison since value is an int PK; transaction_type skips empty choice with `{% if value %}`
- `templates/transactions/transaction_confirm_delete.html` — same centered max-w-lg card pattern as category/account confirm_delete; secondary warning note mentions account balance recalculation

Active sidebar detection pattern:
- Dashboard: `request.resolver_match.url_name == 'dashboard'`
- Other apps: `request.resolver_match.app_name == '<app_name>'`

**Why:** None of the apps had urls.py yet at template creation time — the `{% url ... as var %}{% if var %}` pattern prevents NoReverseMatch errors while URLs are progressively wired up.

**How to apply:** When adding new sidebar links or navbar links, always use the silent `{% url ... as var %}` pattern until the corresponding url is confirmed registered.
