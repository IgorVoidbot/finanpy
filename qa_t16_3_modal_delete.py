"""
QA Test T16.3 - Modal de confirmação de exclusão
Testa os fluxos de exclusão via modal para: Contas, Categorias e Transações
"""
import os
import sys
import json
import time
from playwright.sync_api import sync_playwright, expect

BASE_URL = 'http://127.0.0.1:8000'
SCREENSHOTS_DIR = '/c/Users/ygor/Desktop/projetos/pyfinance/qa_screenshots/t16_3'
EMAIL = 'test@test.com'
PASSWORD = 'testpass123'

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

results = []
console_errors = []


def record(name, passed, expected=None, found=None, screenshot=None, observation=None, logs=None):
    results.append({
        'name': name,
        'passed': passed,
        'expected': expected,
        'found': found,
        'screenshot': screenshot,
        'observation': observation,
        'logs': logs,
    })
    status = 'PASS' if passed else 'FAIL'
    print(f'[{status}] {name}')
    if not passed:
        if expected:
            print(f'       Expected: {expected}')
        if found:
            print(f'       Found:    {found}')
    if observation:
        print(f'       Note:     {observation}')


def screenshot(page, name):
    path = f'{SCREENSHOTS_DIR}/{name}.png'
    page.screenshot(path=path)
    return path


def login(page):
    page.goto(f'{BASE_URL}/login/')
    page.fill('[name="username"]', EMAIL)
    page.fill('[name="password"]', PASSWORD)
    page.click('[type="submit"]')
    page.wait_for_url(f'{BASE_URL}/dashboard/', timeout=5000)


def ensure_account(page, name='Conta QA Modal', account_type='checking', balance='1000.00'):
    """Create account if it doesn't exist; return its pk."""
    page.goto(f'{BASE_URL}/contas/')
    page.wait_for_load_state('networkidle')
    if name in page.content():
        # find pk via delete button data-delete-url
        buttons = page.query_selector_all('button[data-delete-url*="/contas/"]')
        for btn in buttons:
            row_el = btn.evaluate_handle('el => el.closest("tr")')
            if row_el:
                row_text = page.evaluate('el => el ? el.textContent : ""', row_el)
                if row_text and name in row_text:
                    url = btn.get_attribute('data-delete-url')
                    digits = [p for p in url.split('/') if p.isdigit()]
                    if digits:
                        return digits[0]
    # create
    page.goto(f'{BASE_URL}/contas/nova/')
    page.fill('[name="name"]', name)
    page.select_option('[name="account_type"]', account_type)
    page.fill('[name="initial_balance"]', balance)
    page.click('[type="submit"]')
    page.wait_for_url(f'{BASE_URL}/contas/', timeout=5000)
    page.wait_for_load_state('networkidle')
    buttons = page.query_selector_all('button[data-delete-url*="/contas/"]')
    for btn in buttons:
        row_el = btn.evaluate_handle('el => el.closest("tr")')
        if row_el:
            row_text = page.evaluate('el => el ? el.textContent : ""', row_el)
            if row_text and name in row_text:
                url = btn.get_attribute('data-delete-url')
                digits = [p for p in url.split('/') if p.isdigit()]
                if digits:
                    return digits[0]
    return None


def ensure_category(page, name='Categoria QA Modal', cat_type='expense'):
    """Create category if needed; return pk."""
    page.goto(f'{BASE_URL}/categorias/')
    page.wait_for_load_state('networkidle')
    if name in page.content():
        buttons = page.query_selector_all('button[data-delete-url*="/categorias/"]')
        for btn in buttons:
            row_el = btn.evaluate_handle('el => el.closest("tr")')
            if row_el:
                row_text = page.evaluate('el => el ? el.textContent : ""', row_el)
                if row_text and name in row_text:
                    url = btn.get_attribute('data-delete-url')
                    digits = [p for p in url.split('/') if p.isdigit()]
                    if digits:
                        return digits[0]
    page.goto(f'{BASE_URL}/categorias/nova/')
    page.fill('[name="name"]', name)
    page.select_option('[name="transaction_type"]', cat_type)
    page.click('[type="submit"]')
    page.wait_for_url(f'{BASE_URL}/categorias/', timeout=5000)
    page.wait_for_load_state('networkidle')
    buttons = page.query_selector_all('button[data-delete-url*="/categorias/"]')
    for btn in buttons:
        row_el = btn.evaluate_handle('el => el.closest("tr")')
        if row_el:
            row_text = page.evaluate('el => el ? el.textContent : ""', row_el)
            if row_text and name in row_text:
                url = btn.get_attribute('data-delete-url')
                digits = [p for p in url.split('/') if p.isdigit()]
                if digits:
                    return digits[0]
    return None


def ensure_transaction(page, description='Transacao QA Modal'):
    """Create a transaction to be deleted; return pk."""
    page.goto(f'{BASE_URL}/transacoes/')
    page.wait_for_load_state('networkidle')
    if description in page.content():
        buttons = page.query_selector_all('button[data-delete-url*="/transacoes/"]')
        for btn in buttons:
            row_el = btn.evaluate_handle('el => el.closest("tr")')
            if row_el:
                row_text = page.evaluate('el => el ? el.textContent : ""', row_el)
                if row_text and description in row_text:
                    url = btn.get_attribute('data-delete-url')
                    digits = [p for p in url.split('/') if p.isdigit()]
                    if digits:
                        return digits[0]
    page.goto(f'{BASE_URL}/transacoes/nova/')
    page.wait_for_load_state('networkidle')
    # select first account and category
    page.select_option('[name="account"]', index=1)
    page.select_option('[name="category"]', index=1)
    page.fill('[name="description"]', description)
    page.fill('[name="amount"]', '50.00')
    page.fill('[name="date"]', '2026-04-05')
    page.click('[type="submit"]')
    page.wait_for_url(f'{BASE_URL}/transacoes/', timeout=5000)
    page.wait_for_load_state('networkidle')
    buttons = page.query_selector_all('button[data-delete-url*="/transacoes/"]')
    for btn in buttons:
        row_el = btn.evaluate_handle('el => el.closest("tr")')
        if row_el:
            row_text = page.evaluate('el => el ? el.textContent : ""', row_el)
            if row_text and description in row_text:
                url = btn.get_attribute('data-delete-url')
                digits = [p for p in url.split('/') if p.isdigit()]
                if digits:
                    return digits[0]
    return None


def get_delete_button(page, entity_url_fragment, item_name=None):
    """Return delete button matching entity URL. If item_name given, find the button in that row."""
    buttons = page.query_selector_all(f'button[data-delete-url*="{entity_url_fragment}"]')
    if not buttons:
        return None
    if not item_name:
        return buttons[0]
    # Try to find the button whose row contains item_name
    for btn in buttons:
        # Check data-modal-body attribute first (faster)
        body_attr = btn.get_attribute('data-modal-body') or ''
        if item_name in body_attr:
            return btn
        # Fallback: check the row text
        row_el = btn.evaluate_handle('el => el.closest("tr")')
        if row_el:
            row_text = page.evaluate('el => el ? el.textContent : ""', row_el)
            if row_text and item_name in row_text:
                return btn
    # fallback to first if none matched
    return buttons[0]


def modal_is_visible(page):
    modal = page.query_selector('#modal-confirm')
    if not modal:
        return False
    return 'hidden' not in (modal.get_attribute('class') or '')


def modal_is_hidden(page):
    modal = page.query_selector('#modal-confirm')
    if not modal:
        return True
    return 'hidden' in (modal.get_attribute('class') or '')


def test_modal_for_entity(page, entity_name, list_url, url_fragment, item_name):
    """
    Runs all modal sub-tests for a given entity.
    entity_name: display name like 'Conta', 'Categoria', 'Transação'
    list_url: URL of the list page
    url_fragment: fragment to identify delete buttons, e.g. '/contas/'
    item_name: name shown on the item row
    """
    print(f'\n=== Testing modal for: {entity_name} ===')

    # --- Test 1: Modal opens (does not navigate away) ---
    page.goto(list_url)
    page.wait_for_load_state('networkidle')
    current_url_before = page.url
    screenshot(page, f'{entity_name.lower()}_01_list_before')

    btn = get_delete_button(page, url_fragment, item_name)
    if not btn:
        record(
            f'{entity_name} - Modal abre ao clicar Excluir',
            False,
            expected='Botão Excluir presente na lista',
            found='Nenhum botão com data-delete-url encontrado',
            screenshot=f'{entity_name.lower()}_01_list_before.png',
        )
        return  # skip remaining tests for this entity

    btn.click()
    time.sleep(0.3)
    screenshot(page, f'{entity_name.lower()}_02_modal_open')

    url_unchanged = page.url == current_url_before
    modal_visible = modal_is_visible(page)

    record(
        f'{entity_name} - Modal abre ao clicar Excluir (sem navegar)',
        url_unchanged and modal_visible,
        expected='Modal visível, URL inalterada',
        found=f'URL={"inalterada" if url_unchanged else "mudou para "+page.url}, modal={"visível" if modal_visible else "oculto"}',
        screenshot=f'{entity_name.lower()}_02_modal_open.png',
    )

    if not modal_visible:
        # Can't proceed with modal tests
        return

    # --- Test 2: Correct content ---
    title_el = page.query_selector('#modal-confirm-title')
    body_el = page.query_selector('#modal-confirm-body')
    warning_el = page.query_selector('#modal-confirm-warning')

    title_text = title_el.inner_text() if title_el else ''
    body_text = body_el.inner_text() if body_el else ''
    warning_text = warning_el.inner_text() if warning_el else ''

    has_title = bool(title_text.strip())
    has_body = bool(body_text.strip())
    has_warning = bool(warning_text.strip())
    item_in_body = item_name in body_text if item_name else True

    record(
        f'{entity_name} - Conteúdo do modal correto',
        has_title and has_body and has_warning and item_in_body,
        expected=f'Título preenchido, corpo com "{item_name}", aviso presente',
        found=f'título="{title_text}", corpo="{body_text[:80]}", aviso="{warning_text[:60]}"',
        screenshot=f'{entity_name.lower()}_02_modal_open.png',
    )

    # --- Test 3: Cancel closes modal ---
    cancel_btn = page.query_selector('#modal-confirm-cancel')
    if cancel_btn:
        cancel_btn.click()
        time.sleep(0.2)
        screenshot(page, f'{entity_name.lower()}_03_after_cancel')
        modal_closed = modal_is_hidden(page)
        record(
            f'{entity_name} - Cancelar fecha o modal',
            modal_closed,
            expected='Modal oculto após clicar Cancelar',
            found='Modal oculto' if modal_closed else 'Modal ainda visível',
            screenshot=f'{entity_name.lower()}_03_after_cancel.png',
        )
    else:
        record(f'{entity_name} - Cancelar fecha o modal', False,
               expected='Botão Cancelar presente', found='Não encontrado')

    # Reopen for backdrop test
    page.goto(list_url)
    page.wait_for_load_state('networkidle')
    btn = get_delete_button(page, url_fragment, item_name)
    btn.click()
    time.sleep(0.3)

    # --- Test 4: Backdrop closes modal ---
    # Click on the backdrop (modal overlay but outside the panel)
    modal_el = page.query_selector('#modal-confirm')
    modal_el.click(position={'x': 5, 'y': 5})
    time.sleep(0.2)
    screenshot(page, f'{entity_name.lower()}_04_after_backdrop')
    modal_closed = modal_is_hidden(page)
    record(
        f'{entity_name} - Clicar no backdrop fecha o modal',
        modal_closed,
        expected='Modal oculto após clicar no backdrop',
        found='Modal oculto' if modal_closed else 'Modal ainda visível',
        screenshot=f'{entity_name.lower()}_04_after_backdrop.png',
    )

    # Reopen for Escape test
    page.goto(list_url)
    page.wait_for_load_state('networkidle')
    btn = get_delete_button(page, url_fragment, item_name)
    btn.click()
    time.sleep(0.3)

    # --- Test 5: Escape closes modal ---
    page.keyboard.press('Escape')
    time.sleep(0.2)
    screenshot(page, f'{entity_name.lower()}_05_after_escape')
    modal_closed = modal_is_hidden(page)
    record(
        f'{entity_name} - Tecla Escape fecha o modal',
        modal_closed,
        expected='Modal oculto após pressionar Escape',
        found='Modal oculto' if modal_closed else 'Modal ainda visível',
        screenshot=f'{entity_name.lower()}_05_after_escape.png',
    )

    # --- Test 6: Confirm deletion ---
    page.goto(list_url)
    page.wait_for_load_state('networkidle')
    content_before = page.content()
    btn = get_delete_button(page, url_fragment, item_name)
    delete_url = btn.get_attribute('data-delete-url') if btn else None
    btn.click()
    time.sleep(0.3)

    # submit the form
    submit_btn = page.query_selector('#modal-confirm-form [type="submit"]')
    if submit_btn:
        submit_btn.click()
        try:
            page.wait_for_url(lambda url: True, timeout=5000)
        except Exception:
            pass
        page.wait_for_load_state('networkidle')
        time.sleep(0.3)
        screenshot(page, f'{entity_name.lower()}_06_after_delete')

        final_url = page.url
        final_content = page.content()

        # Item should no longer be in the list
        item_gone = item_name not in final_content
        # Check for success message
        has_success = (
            'exclu' in final_content.lower()
            or 'sucesso' in final_content.lower()
            or 'removid' in final_content.lower()
        )

        record(
            f'{entity_name} - Confirmar exclusão remove o item',
            item_gone,
            expected=f'"{item_name}" não aparece mais na lista',
            found=f'Item {"removido" if item_gone else "ainda presente"} na lista',
            screenshot=f'{entity_name.lower()}_06_after_delete.png',
            observation=f'Mensagem de sucesso: {"presente" if has_success else "não encontrada"}',
        )

        record(
            f'{entity_name} - Mensagem de sucesso exibida após exclusão',
            has_success,
            expected='Texto de sucesso/exclusão visível na página',
            found='Presente' if has_success else 'Ausente',
            screenshot=f'{entity_name.lower()}_06_after_delete.png',
        )
    else:
        record(f'{entity_name} - Confirmar exclusão', False,
               expected='Botão Excluir no formulário modal', found='Não encontrado')


def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = context.new_page()

        # Capture console errors
        page.on('console', lambda msg: console_errors.append(
            f'[{msg.type}] {msg.text}') if msg.type in ('error', 'warning') else None)

        # ---- Login ----
        print('Logging in...')
        try:
            login(page)
            print(f'Login OK — current URL: {page.url}')
        except Exception as e:
            print(f'Login FAILED: {e}')
            screenshot(page, 'login_failed')
            browser.close()
            return

        # ---- Prepare test data ----
        print('\nPreparing test data...')

        # Account for deletion
        account_pk = ensure_account(page, 'Conta QA Para Excluir', 'savings', '500.00')
        print(f'Account PK: {account_pk}')

        # Account to stay (for transaction/category tests)
        _ = ensure_account(page, 'Conta QA Permanente', 'checking', '200.00')

        # Category for deletion
        category_pk = ensure_category(page, 'Categoria QA Para Excluir', 'expense')
        print(f'Category PK: {category_pk}')

        # Transaction for deletion
        transaction_pk = ensure_transaction(page, 'Transacao QA Para Excluir')
        print(f'Transaction PK: {transaction_pk}')

        # ---- Run modal tests ----
        test_modal_for_entity(
            page,
            entity_name='Conta',
            list_url=f'{BASE_URL}/contas/',
            url_fragment='/contas/',
            item_name='Conta QA Para Excluir',
        )

        # After account deletion we need to recreate a category to delete
        # (it may have been tied to the deleted account's transactions)
        category_pk2 = ensure_category(page, 'Categoria QA Para Excluir 2', 'income')
        print(f'Category2 PK: {category_pk2}')

        test_modal_for_entity(
            page,
            entity_name='Categoria',
            list_url=f'{BASE_URL}/categorias/',
            url_fragment='/categorias/',
            item_name='Categoria QA Para Excluir 2',
        )

        # Create a fresh transaction for deletion
        transaction_pk2 = ensure_transaction(page, 'Transacao QA Para Excluir 2')
        print(f'Transaction2 PK: {transaction_pk2}')

        test_modal_for_entity(
            page,
            entity_name='Transacao',
            list_url=f'{BASE_URL}/transacoes/',
            url_fragment='/transacoes/',
            item_name='Transacao QA Para Excluir 2',
        )

        # ---- Console errors ----
        print('\n--- Console errors captured ---')
        js_errors = [e for e in console_errors if '[error]' in e]
        if js_errors:
            for e in js_errors:
                print(e)
        else:
            print('Nenhum erro de console detectado.')

        browser.close()

    # ---- Print report ----
    print('\n' + '='*60)
    print('RELATORIO FINAL — T16.3 Modal de Confirmação de Exclusão')
    print('='*60)

    passed = [r for r in results if r['passed']]
    failed = [r for r in results if not r['passed']]

    for r in results:
        icon = 'OK' if r['passed'] else 'FAIL'
        print(f'\n[{icon}] {r["name"]}')
        if r.get('screenshot'):
            print(f'     Screenshot: {r["screenshot"]}')
        if r.get('observation'):
            print(f'     Observacao: {r["observation"]}')
        if not r['passed']:
            if r.get('expected'):
                print(f'     Esperado: {r["expected"]}')
            if r.get('found'):
                print(f'     Encontrado: {r["found"]}')

    print(f'\nTotal: {len(results)} | Passaram: {len(passed)} | Falharam: {len(failed)}')

    if failed:
        print('\n--- Itens que precisam de correcao ---')
        for r in failed:
            print(f'  * {r["name"]}')
            if r.get('expected'):
                print(f'    Esperado: {r["expected"]}')
            if r.get('found'):
                print(f'    Encontrado: {r["found"]}')

    if js_errors:
        print('\n--- Erros JavaScript detectados ---')
        for e in js_errors:
            print(f'  {e}')

    # Save JSON summary
    summary_path = f'{SCREENSHOTS_DIR}/results.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(results),
            'passed': len(passed),
            'failed': len(failed),
            'results': results,
            'console_errors': console_errors,
        }, f, ensure_ascii=False, indent=2)
    print(f'\nResultados salvos em: {summary_path}')


if __name__ == '__main__':
    run_tests()
