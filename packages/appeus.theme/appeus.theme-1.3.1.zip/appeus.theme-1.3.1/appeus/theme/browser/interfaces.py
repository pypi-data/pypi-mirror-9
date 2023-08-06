from zope.interface import Interface
from appeus.theme import themeMessageFactory as _
from zope import schema
from plonetheme.bootstrap.browser.interfaces import IThemeSpecific as IDefaultPloneLayer


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "APP.EUS Theme" theme, this interface must be its layer
       (in theme/viewlets/configure.zcml).
    """


class IAppEusFeaturedApp(Interface):
    """ Control Panel to selected the featured APP
    """
    featured_app = schema.Choice(
        title=_(u"Featured App"),
        vocabulary="appeus.content.apps",
        default=u"",
        required=True)
