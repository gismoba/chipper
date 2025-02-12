from django import template

register = template.Library()

@register.filter(name='mask_password')
def mask_password(value):
    if len(value) > 2:
        return value[:2] + '*' * (len(value) - 2)
    return value

