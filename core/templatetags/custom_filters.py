from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtracts the arg from the value."""
    try:
        return value - arg
    except (ValueError, TypeError):
        try:
            return value or 0
        except:
            return 0

@register.filter
def divisibleby(value, arg):
    """
    Returns the percentage value/arg * 100
    """
    try:
        value = int(value)
        arg = int(arg)
        if arg:
            return (value / arg) * 100
        return 0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0