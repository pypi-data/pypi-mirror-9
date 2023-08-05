"""
Register the theme.
"""
from django_diazo.theme import DiazoTheme, registry


class BlueTheme(DiazoTheme):
    name = 'Blue'
    slug = 'blue'
    pattern = '^(?!.*admin)'  # everything but /admin/


registry.register(BlueTheme)
