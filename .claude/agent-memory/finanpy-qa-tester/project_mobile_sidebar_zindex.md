---
name: Mobile Sidebar Z-Index Bug and Fix
description: Drawer panel close button was blocked by navbar at same z-50 level; fixed by raising overlay/panel to z-60/z-70
type: project
---

## Bug discovered during T15.3 (2026-04-05)

The mobile sidebar drawer panel (z-50) conflicted with the sticky navbar (also z-50). At 320px width, the close button in the drawer header at x=243,y=16 was intercepted by the navbar's right section (greeting + logout link). Playwright `page.click('#mobile-sidebar-close')` timed out with "subtree intercepts pointer events".

**Fix applied in `templates/base_app.html`:**
- Overlay: `z-40` → `z-[60]`
- Drawer panel: `z-50` → `z-[70]`

This ensures the panel is always above the navbar (`z-50`) regardless of screen width.

**How to apply:** When adding overlays/drawers to Tailwind, use `z-[60]`/`z-[70]` for overlays that must stack above `z-50` sticky navbars. Standard `z-50` is not sufficient when the navbar also uses `z-50`.
