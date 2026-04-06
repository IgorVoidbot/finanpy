"""
T15.3 — Responsiveness test for Finanpy across screen sizes.
Tests mobile sidebar (hamburger), tablet breakpoint, and desktop layout.

Note: base_app.html wraps sidebar.html in <aside class="hidden md:block...">.
sidebar.html itself is also an <aside> element — so there are 2 aside elements.
We target the outer wrapper (first) to check visibility via Tailwind responsive classes.
The correct check is whether the outer wrapper has display:none (Tailwind hidden class).
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = 'http://127.0.0.1:8000'
EMAIL = 'teste@finanpy.com'
PASSWORD = 'TesteSenha123'

SCREENSHOTS_DIR = Path('C:/Users/ygor/Desktop/projetos/pyfinance/qa_screenshots/t15_3')
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PAGES = [
    ('dashboard', '/dashboard/'),
    ('contas', '/contas/'),
    ('categorias', '/categorias/'),
    ('transacoes', '/transacoes/'),
    ('perfil', '/perfil/'),
]

results = []


def log(status, name, details='', extra=''):
    symbol = 'PASS' if status else 'FAIL'
    entry = {'status': status, 'name': name, 'details': details, 'extra': extra}
    results.append(entry)
    print(f"  [{symbol}] {name}")
    if details:
        print(f"         {details}")
    if extra:
        print(f"         {extra}")


def screenshot(page, name):
    path = SCREENSHOTS_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=False)
    return str(path)


def do_login(page):
    page.goto(f'{BASE_URL}/login/')
    page.fill('input[type="email"]', EMAIL)
    page.fill('input[type="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url('**/dashboard/**', timeout=8000)
    page.wait_for_load_state('networkidle')


def is_element_actually_visible(page, selector):
    """Check computed display/visibility to handle Tailwind responsive classes."""
    return page.evaluate(f"""() => {{
        const el = document.querySelector('{selector}');
        if (!el) return null;
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
    }}""")


def run_mobile_tests(page, vp_name, vp):
    print(f"\n  --- {vp_name} ({vp['width']}x{vp['height']}) ---")
    page.set_viewport_size(vp)
    page.goto(f'{BASE_URL}/dashboard/')
    page.wait_for_load_state('networkidle')

    # 1. Hamburger must be visible
    ham_visible = is_element_actually_visible(page, '#menu-toggle')
    log(
        ham_visible is True,
        f'{vp_name} — hamburger button visible',
        f'Expected: visible | computed visible: {ham_visible}'
    )

    # 2. Desktop sidebar wrapper must be hidden (outer aside has hidden md:block)
    aside_visible = is_element_actually_visible(page, 'aside')
    log(
        aside_visible is False,
        f'{vp_name} — desktop sidebar hidden (outer wrapper)',
        f'Expected: hidden | computed visible: {aside_visible}'
    )

    screenshot(page, f'{vp_name}_dashboard_initial')

    # 3. Overlay starts hidden
    overlay_classes = page.get_attribute('#mobile-sidebar-overlay', 'class') or ''
    overlay_hidden_before = 'hidden' in overlay_classes
    log(
        overlay_hidden_before,
        f'{vp_name} — overlay has "hidden" class before click',
        f'Classes: {overlay_classes}'
    )

    # 4. Click hamburger — overlay should open
    page.click('#menu-toggle')
    page.wait_for_timeout(400)

    screenshot(page, f'{vp_name}_sidebar_open')

    overlay_classes_after = page.get_attribute('#mobile-sidebar-overlay', 'class') or ''
    overlay_open = 'hidden' not in overlay_classes_after
    log(
        overlay_open,
        f'{vp_name} — overlay opens after hamburger click',
        f'Classes after click: {overlay_classes_after}'
    )

    # 5. Drawer panel is visible
    panel_visible = is_element_actually_visible(page, '#mobile-sidebar-panel')
    log(
        panel_visible is True,
        f'{vp_name} — drawer panel visible when overlay open',
        f'Panel computed visible: {panel_visible}'
    )

    # 6. Nav links in drawer
    link_count = page.evaluate("""() => document.querySelectorAll('#mobile-sidebar-panel a').length""")
    log(
        link_count >= 5,
        f'{vp_name} — drawer has nav links (found {link_count})',
        f'Expected: >= 5 | Found: {link_count}'
    )

    # 7. Close button hides overlay
    page.click('#mobile-sidebar-close')
    page.wait_for_timeout(400)

    overlay_classes_closed = page.get_attribute('#mobile-sidebar-overlay', 'class') or ''
    overlay_closed = 'hidden' in overlay_classes_closed
    log(
        overlay_closed,
        f'{vp_name} — close button hides overlay',
        f'Classes after close: {overlay_classes_closed}'
    )

    screenshot(page, f'{vp_name}_sidebar_closed')

    # 8. Backdrop click closes overlay
    page.click('#menu-toggle')
    page.wait_for_timeout(400)

    # Click on the backdrop (far right, outside the 72-unit panel ~288px)
    click_x = min(vp['width'] - 10, vp['width'] - 1)
    # Only do backdrop test if viewport is wide enough to have backdrop area
    if vp['width'] > 300:
        page.mouse.click(click_x, vp['height'] // 2)
        page.wait_for_timeout(400)

        overlay_after_backdrop = page.get_attribute('#mobile-sidebar-overlay', 'class') or ''
        backdrop_closed = 'hidden' in overlay_after_backdrop
        log(
            backdrop_closed,
            f'{vp_name} — backdrop click closes overlay',
            f'Classes after backdrop click: {overlay_after_backdrop}'
        )
    else:
        # Close it via button to reset state
        page.click('#mobile-sidebar-close')
        page.wait_for_timeout(300)
        log(True, f'{vp_name} — backdrop test skipped (viewport too narrow for backdrop area)', 'N/A — panel fills entire width')


def run_tablet_desktop_tests(page, vp_name, vp):
    print(f"\n  --- {vp_name} ({vp['width']}x{vp['height']}) ---")
    page.set_viewport_size(vp)
    page.goto(f'{BASE_URL}/dashboard/')
    page.wait_for_load_state('networkidle')

    screenshot(page, f'{vp_name}_dashboard')

    # Hamburger must be hidden
    ham_visible = is_element_actually_visible(page, '#menu-toggle')
    log(
        ham_visible is False,
        f'{vp_name} — hamburger hidden',
        f'Expected: hidden | computed visible: {ham_visible}'
    )

    # Desktop sidebar must be visible
    aside_visible = is_element_actually_visible(page, 'aside')
    log(
        aside_visible is True,
        f'{vp_name} — desktop sidebar visible',
        f'Expected: visible | computed visible: {aside_visible}'
    )

    # Sidebar nav links visible in aside
    link_count = page.evaluate("""() => document.querySelectorAll('aside nav a').length""")
    log(
        link_count >= 5,
        f'{vp_name} — aside has nav links (found {link_count})',
        f'Expected: >= 5 | Found: {link_count}'
    )


def run_overflow_test(page, vp_name, vp, page_name, url):
    page.set_viewport_size(vp)
    page.goto(f'{BASE_URL}{url}')
    page.wait_for_load_state('networkidle')

    screenshot(page, f'{vp_name}_{page_name}')

    overflow = page.evaluate("""() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
    })""")

    has_overflow = overflow['scrollWidth'] > overflow['clientWidth']
    log(
        not has_overflow,
        f'{vp_name} — {page_name}: no horizontal overflow',
        f'scrollWidth={overflow["scrollWidth"]} clientWidth={overflow["clientWidth"]}'
        + (' <<< OVERFLOW' if has_overflow else '')
    )


def run_status_test(page, page_name, url):
    response = page.goto(f'{BASE_URL}{url}')
    status = response.status
    log(
        status == 200,
        f'{page_name} loads HTTP {status}',
        f'URL: {BASE_URL}{url}'
    )


def run_console_test(page, vp_name, page_name, url):
    console_errors = []
    def on_console(msg):
        if msg.type == 'error':
            console_errors.append(msg.text)
    page.on('console', on_console)
    page.goto(f'{BASE_URL}{url}')
    page.wait_for_load_state('networkidle')
    if console_errors:
        log(False, f'{vp_name} — {page_name}: JS console errors', str(console_errors))
    else:
        log(True, f'{vp_name} — {page_name}: no JS console errors')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("\n=== Logging in ===")
    page.set_viewport_size({'width': 1280, 'height': 800})
    do_login(page)
    print("Login successful.\n")

    # ─── MOBILE BREAKPOINTS ───────────────────────────────────────────────────
    print("\n=== MOBILE BREAKPOINT TESTS (hamburger + overlay) ===")
    for vp_name, vp in [
        ('mobile_320', {'width': 320, 'height': 568}),
        ('mobile_375', {'width': 375, 'height': 667}),
        ('mobile_414', {'width': 414, 'height': 896}),
    ]:
        run_mobile_tests(page, vp_name, vp)

    # ─── TABLET (768px = md breakpoint) ──────────────────────────────────────
    print("\n=== TABLET BREAKPOINT TESTS (md: sidebar visible, hamburger hidden) ===")
    run_tablet_desktop_tests(page, 'tablet_768', {'width': 768, 'height': 1024})

    # ─── DESKTOP ─────────────────────────────────────────────────────────────
    print("\n=== DESKTOP BREAKPOINT TESTS ===")
    for vp_name, vp in [
        ('desktop_1024', {'width': 1024, 'height': 768}),
        ('desktop_1440', {'width': 1440, 'height': 900}),
    ]:
        run_tablet_desktop_tests(page, vp_name, vp)

    # ─── LAYOUT / OVERFLOW TESTS ─────────────────────────────────────────────
    print("\n=== LAYOUT / OVERFLOW TESTS (all authenticated pages) ===")
    for vp_name, vp in [
        ('mobile_375', {'width': 375, 'height': 667}),
        ('tablet_768', {'width': 768, 'height': 1024}),
        ('desktop_1440', {'width': 1440, 'height': 900}),
    ]:
        print(f"\n  -- {vp_name} --")
        for page_name, url in PAGES:
            run_overflow_test(page, vp_name, vp, page_name, url)

    # ─── HTTP STATUS ─────────────────────────────────────────────────────────
    print("\n=== HTTP STATUS TESTS ===")
    page.set_viewport_size({'width': 1280, 'height': 800})
    for page_name, url in PAGES:
        run_status_test(page, page_name, url)

    # ─── JS CONSOLE ERRORS ───────────────────────────────────────────────────
    print("\n=== JS CONSOLE ERROR TESTS (mobile) ===")
    page.set_viewport_size({'width': 375, 'height': 667})
    for page_name, url in PAGES:
        run_console_test(page, 'mobile_375', page_name, url)

    browser.close()

# ─── SUMMARY ──────────────────────────────────────────────────────────────────
passed = [r for r in results if r['status']]
failed = [r for r in results if not r['status']]

print("\n" + "=" * 65)
print("T15.3 RESPONSIVENESS TEST SUMMARY")
print("=" * 65)
print(f"Total   : {len(results)}")
print(f"Passed  : {len(passed)}")
print(f"Failed  : {len(failed)}")

if failed:
    print("\nFAILED TESTS:")
    for r in failed:
        print(f"  FAIL  {r['name']}")
        if r['details']:
            print(f"        {r['details']}")
else:
    print("\nAll tests passed.")

print(f"\nScreenshots: {SCREENSHOTS_DIR}")

report_path = SCREENSHOTS_DIR / 'report.json'
with open(str(report_path), 'w', encoding='utf-8') as f:
    json.dump({'passed': len(passed), 'failed': len(failed), 'results': results}, f, indent=2, ensure_ascii=False)
print(f"Report JSON: {report_path}")
