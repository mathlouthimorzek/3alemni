from django import template

register = template.Library()


@register.filter
def get(item, key):
    return item.get(key, 0)
