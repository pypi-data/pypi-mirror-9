from django.conf import settings


DOCTYPE = getattr(
    settings,
    'DIAZO_DOCTYPE',
    None,
)

ALLOWED_CONTENT_TYPES = getattr(
    settings,
    'DIAZO_ALLOWED_CONTENT_TYPES',
    ['text/html', 'application/xhtml+xml', 'text/xml', 'application/xml'],
)
