# -*- coding: utf-8 -*-
from django_diazo.utils import check_themes_enabled


def diazo_enabled(request):
    """
    Adds Diazo enabled variable to the context.
    """
    return {
        'DIAZO_ENABLED': check_themes_enabled(request),
    }
