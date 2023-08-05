import os
from logging import getLogger
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django_diazo.models import Theme
from django_diazo.theme import registry
from django_diazo import autodiscover as django_diazo_autodiscover


django_diazo_autodiscover()

class Command(BaseCommand):
    help = _('Synchronize database with built-in themes that are registered via the registry.')
    requires_model_validation = True

    def handle(self, *args, **options):
        logger = getLogger('django_diazo')
        themes = dict([(t.slug, t) for t in Theme.objects.filter(builtin=True)])
        # Add/modify themes
        for theme in registry.get_themes():
            path = theme.slug
            url = settings.STATIC_URL + theme.slug
            if theme.prefix:
                path = os.path.join(path, theme.prefix)
                url += '/' + theme.prefix
            if theme.slug in themes:
                themes[theme.slug].path = path
                themes[theme.slug].url = url
                themes[theme.slug].prefix = theme.prefix
                themes[theme.slug].pattern = theme.pattern
                themes[theme.slug].save()
                themes.pop(theme.slug)
                logger.info('Synced theme with name \'{0}\'.'.format(theme.name))
            else:
                Theme.objects.create(
                    name=theme.name,
                    slug=theme.slug,
                    prefix=theme.prefix,
                    path=path,
                    url=url,
                    builtin=True,
                    pattern=theme.pattern
                )
                logger.info('Added new theme with name \'{0}\'.'.format(theme.name))
        # Delete themes
        for name, theme in themes.items():
            theme.delete()
            logger.info('Deleted theme with name \'{0}\'.'.format(name))
        logger.info('Done syncing built-in themes.')
