from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """Divide el valor por el argumento"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def to_list(value):
    """Convierte un QuerySet o iterable a lista"""
    try:
        return list(value)
    except (TypeError, ValueError):
        return []


@register.filter
def sum(value, arg):
    """Suma los valores de un campo en una lista de objetos"""
    try:
        total = 0
        for item in value:
            attr_value = getattr(item, arg, 0)
            if attr_value:
                total += float(attr_value)
        return total
    except (TypeError, ValueError, AttributeError):
        return 0
