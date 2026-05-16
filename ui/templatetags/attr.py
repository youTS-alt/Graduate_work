from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def attr(obj, name: str):
    return getattr(obj, name, '')

