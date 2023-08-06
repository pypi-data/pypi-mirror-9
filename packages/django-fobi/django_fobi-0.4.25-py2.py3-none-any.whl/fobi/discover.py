__title__ = 'fobi.discover'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014-2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('autodiscover',)

import imp
import logging

from django.conf import settings

from nine.versions import DJANGO_GTE_1_7

logger = logging.getLogger(__file__)

# In Django a dotted path can be used up to the app config class. In
# such cases the old-school autodiscovery of modules doesn't work but we
# have a great Django `autodiscover_modules` tool then. In cases if Django 
# version is >= 1.7, we use the Django `autodiscover_modules` tool falling back
# to our own implementation of it otherwise.
if DJANGO_GTE_1_7:
    from django.utils.module_loading import autodiscover_modules
else:
    def autodiscover_modules(module_name):
        for app in settings.INSTALLED_APPS:
            try:
                app = str(app)
                app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
            except (AttributeError, TypeError) as e:
                logger.debug(str(e))
                continue

            try:
                imp.find_module(module_name, app_path)
            except ImportError as e:
                logger.debug(str(e))
                continue
            __import__('{0}.{1}'.format(app, module_name))

from fobi.conf import get_setting

def autodiscover():
    """
    Autodiscovers files that should be found by fobi.
    """
    FORM_ELEMENT_PLUGINS_MODULE_NAME = get_setting(
        'FORM_ELEMENT_PLUGINS_MODULE_NAME'
        )
    FORM_HANDLER_PLUGINS_MODULE_NAME = get_setting(
        'FORM_HANDLER_PLUGINS_MODULE_NAME'
        )
    THEMES_MODULE_NAME = get_setting(
        'THEMES_MODULE_NAME'
        )
    FORM_CALLBACKS_MODULE_NAME = get_setting(
        'FORM_CALLBACKS_MODULE_NAME'
        )

    #FORM_IMPORTER_PLUGINS_MODULE_NAME = get_setting(
    #    'FORM_IMPORTER_PLUGINS_MODULE_NAME'
    #    )

    # Discover modules
    autodiscover_modules(FORM_ELEMENT_PLUGINS_MODULE_NAME)
    autodiscover_modules(FORM_HANDLER_PLUGINS_MODULE_NAME)
    autodiscover_modules(THEMES_MODULE_NAME)
    autodiscover_modules(FORM_CALLBACKS_MODULE_NAME)

    # Do not yet discover form importers
    #autodiscover_modules(FORM_IMPORTER_PLUGINS_MODULE_NAME)
