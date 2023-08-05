
class DjangoCmsDiazoMiddleware(object):
    """
    Django CMS 3 add-on
    """

    def process_request(self, request):
        """
        Toggle theme enabled boolean
        """
        if request.user.is_staff:
            if 'theme_on' in request.GET and not request.session.get('django_diazo_theme_enabled', False):
                request.session['django_diazo_theme_enabled'] = True
            if 'theme_off' in request.GET and request.session.get('django_diazo_theme_enabled', True):
                request.session['django_diazo_theme_enabled'] = False
