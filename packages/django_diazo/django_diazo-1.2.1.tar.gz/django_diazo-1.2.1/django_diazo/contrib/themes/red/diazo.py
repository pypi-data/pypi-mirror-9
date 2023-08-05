"""
Register the theme.
"""
from django_diazo.theme import DiazoTheme, registry


class RedTheme(DiazoTheme):
    name = 'Red'
    slug = 'red'


registry.register(RedTheme)
