from django import template

register = template.Library()


@register.filter
def currency_brl(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 'R$ 0,00'
    formatted = '{:,.2f}'.format(value)
    # Convert from en-US format (1,234.56) to pt-BR format (1.234,56)
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {formatted}'
