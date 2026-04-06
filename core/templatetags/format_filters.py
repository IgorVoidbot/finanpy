from django import template
from decimal import Decimal

register = template.Library()


@register.filter(name='brl_currency')
def brl_currency(value):
    """Formata um valor Decimal ou numérico para o formato R$ X.XXX,XX"""
    try:
        value = Decimal(str(value))
        formatted = f'{value:,.2f}'
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'R$ {formatted}'
    except (ValueError, TypeError):
        return 'R$ 0,00'


@register.simple_tag(takes_context=True)
def active_link(context, url_name, active_class='text-emerald-400 bg-emerald-500/10', inactive_class=''):
    """Retorna active_class se a view atual corresponde a url_name, caso contrário inactive_class."""
    from django.urls import resolve, NoReverseMatch
    request = context.get('request')
    if not request:
        return inactive_class
    try:
        current = resolve(request.path_info)
        if current.url_name == url_name or current.view_name == url_name:
            return active_class
    except Exception:
        pass
    return inactive_class
