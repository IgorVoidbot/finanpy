---
name: Finanpy Django Admin Behavior Notes
description: Observed admin behavior including redirect quirks and confirmed working flows
type: project
---

## LOGIN_REDIRECT_URL quirk
After login at /admin/login/ without a `next` param, Django redirects to `/accounts/profile/` (404), NOT to `/admin/`. This is because LOGIN_REDIRECT_URL is not set to `/admin/` in settings. The workaround: after getting a sessionid cookie, navigate directly to `/admin/` in a second request.

**Why:** The project uses a custom auth flow and the admin login does not override LOGIN_REDIRECT_URL.
**How to apply:** In automated HTTP-based tests, always make two requests: one POST to /admin/login/, capture the session cookie, then GET /admin/ directly.

## Admin user creation (add_fieldsets)
- add_fieldsets contains: email, first_name, last_name, password1, password2
- No username field (correctly removed since USERNAME_FIELD = 'email')
- Successful creation redirects to /admin/users/user/{id}/change/

## list_display confirmed working
list_display = ['email', 'first_name', 'last_name', 'is_active'] renders as 5 columns in the table (checkbox + 4 data columns): E-mail, Nome, Sobrenome, Ativo.
is_active shows as icon-yes.svg (green checkmark) for active users.
