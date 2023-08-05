from diazo.wsgi import asbool, DIAZO_OFF_HEADER
from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

from django_diazo.models import Theme
from django_diazo.settings import DOCTYPE, ALLOWED_CONTENT_TYPES


def get_active_theme(request):
    if request.GET.get('theme', None):
        try:
            theme = request.GET.get('theme')
            return Theme.objects.get(pk=theme)
        except Theme.DoesNotExist:
            pass
        except ValueError:
            pass
    for theme in Theme.objects.filter(enabled=True).order_by('sort'):
        if theme.available(request):
            return theme
    return None


def check_themes_enabled(request):
        """
        Check if themes are enabled for the current session/request.
        """
        if request.GET.get('theme', None) == 'none' and (request.user.is_staff or settings.DEBUG):
            return False
        return request.session.get('django_diazo_theme_enabled', True)


def should_transform(process_response):
    """
    Determine if we should transform the response
    """
    def inner_func(request, response):
        if asbool(response.get(DIAZO_OFF_HEADER, 'no')):
            return response

        content_type = response.get('Content-Type', '')
        if not content_type:
            return response

        no_diazo = True
        for content_type in ALLOWED_CONTENT_TYPES:
            if content_type in response.get('Content-Type', ''):
                no_diazo = False
                break
        if no_diazo:
            return response

        content_encoding = response.get('Content-Encoding')
        if content_encoding in ('zip', 'deflate', 'compress',):
            return response

        if 300 <= response.status_code <= 399 or response.status_code in [204, 401]:
            return response

        if len(response.content) == 0:
            return response

        return process_response(request, response)
    return inner_func
