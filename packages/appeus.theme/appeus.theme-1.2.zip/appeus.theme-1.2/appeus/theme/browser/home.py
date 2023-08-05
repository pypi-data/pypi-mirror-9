from .interfaces import IAppEusFeaturedApp
from five import grok
from plone import api
from plone.app.contenttypes.interfaces import ICollection
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


grok.templatedir('templates')


class Home(grok.View):
    grok.context(ICollection)
    grok.require('zope2.View')
    grok.name('home')

    def get_selected_app(self):
        registry = getUtility(IRegistry)
        appeus_config = registry.forInterface(IAppEusFeaturedApp)
        featured = appeus_config.featured_app
        if featured:
            catalog = api.portal.get_tool('portal_catalog')
            content_items = catalog(UID=featured)
            if content_items:
                return content_items[0].getObject()

        return None
