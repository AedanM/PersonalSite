from django import template
from django.conf import settings as django_settings

register = template.Library()


@register.filter
def split(obj, op) -> list:
    return sorted(obj.split(op))
