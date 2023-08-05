from cms.api import get_page_draft
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.constants import RIGHT
from cms.toolbar.items import TemplateItem

from django_diazo.utils import check_themes_enabled


@toolbar_pool.register
class DjangoDiazoSwitchToolbar(CMSToolbar):
    """
    Add Django CMS 3 on/off switch to toolbar
    """
    def populate(self):
        # always use draft if we have a page
        self.page = get_page_draft(self.request.current_page)

        if not self.page:
            # Nothing to do
            return

        self.toolbar.add_item(
            TemplateItem(
                "cms/toolbar/items/on_off.html",
                extra_context={
                    'request': self.request,
                    'diazo_enabled': check_themes_enabled(self.request),
                },
                side=RIGHT,
            ),
            len(self.toolbar.right_items),
        )
