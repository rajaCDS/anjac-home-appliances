from django import template

register = template.Library()

@register.filter
def status_color(status):
    return {
        'pending': 'pending',
        'shipped': 'shipped',
        'delivered': 'delivered',
        'cancelled': 'cancelled',
    }.get(status, 'secondary')
