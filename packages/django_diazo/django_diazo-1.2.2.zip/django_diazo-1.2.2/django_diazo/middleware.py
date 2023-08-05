import os
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from diazo.wsgi import DiazoMiddleware
from diazo.utils import quote_param
from logging import getLogger
from lxml import etree
from lxml.etree import tostring
from repoze.xmliter.serializer import XMLSerializer

from django_diazo.settings import DOCTYPE
from django_diazo.utils import get_active_theme, check_themes_enabled, should_transform


class DjangoDiazoMiddleware(object):
    """
    Django middleware wrapper for Diazo in Django.
    """

    def __init__(self):
        self.app = None
        self.theme_id = None
        self.diazo = None
        self.transform = None
        self.params = {}

    @method_decorator(should_transform)
    def process_response(self, request, response):
        """
        Transform the response with Diazo if transformable
        """
        content = response
        if check_themes_enabled(request):
            theme = get_active_theme(request)
            if theme:
                rules_file = os.path.join(theme.theme_path(), 'rules.xml')
                if theme.id != self.theme_id or not os.path.exists(rules_file) or theme.debug:
                    if not theme.builtin:
                        if theme.rules:
                            fp = open(rules_file, 'w')
                            try:
                                fp.write(theme.rules.serialize())
                            finally:
                                fp.close()

                    self.theme_id = theme.id

                    self.diazo = DiazoMiddleware(
                        app=self.app,
                        global_conf=None,
                        rules=rules_file,
                        prefix=theme.theme_url(),
                        doctype=DOCTYPE,
                    )
                    compiled_theme = self.diazo.compile_theme()
                    self.transform = etree.XSLT(compiled_theme, access_control=self.diazo.access_control)
                    self.params = {}
                    for key, value in self.diazo.environ_param_map.items():
                        if key in request.environ:
                            if value in self.diazo.unquoted_params:
                                self.params[value] = request.environ[key]
                            else:
                                self.params[value] = quote_param(request.environ[key])

                try:
                    if isinstance(response, etree._Element):
                        response = HttpResponse()
                    else:
                        parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True)
                        content = etree.fromstring(response.content, parser)
                    result = self.transform(content, **self.params)
                    response.content = XMLSerializer(result, doctype=DOCTYPE).serialize()
                except Exception, e:
                    getLogger('django_diazo').error(e)
        if isinstance(response, etree._Element):
            response = HttpResponse('<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(content))
        return response
