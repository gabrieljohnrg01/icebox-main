from django import template

register = template.Library()

@register.filter
def percentage(value, arg):
    try:
        if not arg: return 0
        return int((value / arg) * 100)
    except (ValueError, ZeroDivisionError):
        return 0
