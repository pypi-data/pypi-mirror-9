from plone.app.registry.browser.controlpanel import RegistryEditForm
from .interfaces import IAppEusFeaturedApp


class AppEusConfigurationForm(RegistryEditForm):
    schema = IAppEusFeaturedApp
