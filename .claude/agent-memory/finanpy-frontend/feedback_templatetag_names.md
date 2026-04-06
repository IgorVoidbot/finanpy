---
name: Correct templatetag filter and tag names in format_filters
description: The brl_currency filter is named brl_currency (not currency_brl) — templates previously used the wrong name
type: feedback
---

The filter registered in `core/templatetags/format_filters.py` is `brl_currency`, not `currency_brl`. Earlier templates were written with `currency_brl` which would silently fail (render nothing). Always use `{{ value|brl_currency }}`.

The `active_link` simple tag accepts a `view_name` string. For namespaced URLs pass the full dotted name (e.g. `'accounts:account_list'`); for root URLs pass just the name (e.g. `'dashboard'`). It compares against both `resolver.url_name` and `resolver.view_name`.

**Why:** Templates were written before the filter name was finalized, causing a mismatch that would silently produce empty output at runtime.

**How to apply:** Any time you write `|brl_currency` or `{% active_link %}`, verify the exact names in `core/templatetags/format_filters.py` before committing.
