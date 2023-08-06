"""
- `RESTRICT_PLUGIN_ACCESS` (bool): If set to True, (Django) permission system
  for fobi plugins is enabled.
- `FORM_ELEMENT_PLUGINS_MODULE_NAME` (str): Name of the module to placed in 
  the (external) apps in which the fobi form element plugin code should be
  implemented and registered.
- `FORM_HANDLER_PLUGINS_MODULE_NAME` (str): Name of the module to placed in 
  the (external) apps in which the fobi form handler plugin code should be
  implemented and registered.
- `FORM_CALLBACKS_MODULE_NAME` (str): Name of the module to placed in the 
  (external) apps in which the fobi form callback code should be implemented
  and registered.
- `FORM_HANDLER_PLUGINS_EXECUTION_ORDER` (tuple): Order in which the form 
  handler plugins are to be executed.
- `DEBUG`
"""
__title__ = 'fobi.settings'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'RESTRICT_PLUGIN_ACCESS', 'FORM_ELEMENT_PLUGINS_MODULE_NAME',
    'FORM_HANDLER_PLUGINS_MODULE_NAME', 'FORM_IMPORTER_PLUGINS_MODULE_NAME',
    'FORM_CALLBACKS_MODULE_NAME', 'THEMES_MODULE_NAME', 'DEFAULT_THEME',
    'DISPLAY_AUTH_LINK', 'DEBUG', 'GET_PARAM_INITIAL_DATA',

    'CUSTOM_THEME_DATA', 'THEME_FOOTER_TEXT',

    'DEFAULT_MAX_LENGTH', 'FORM_HANDLER_PLUGINS_EXECUTION_ORDER',
    'FAIL_ON_MISSING_FORM_ELEMENT_PLUGINS',
    'FAIL_ON_MISSING_FORM_HANDLER_PLUGINS',
    'FAIL_ON_ERRORS_IN_FORM_ELEMENT_PLUGINS',
    'FAIL_ON_ERRORS_IN_FORM_HANDLER_PLUGINS',

    'WAIT_BETWEEN_TEST_STEPS', 'WAIT_AT_TEST_END',
)

from fobi.conf import get_setting
from fobi.exceptions import NoDefaultThemeSet

# **************************************************************
# **************************************************************
# *************************** Core *****************************
# **************************************************************
# **************************************************************
RESTRICT_PLUGIN_ACCESS = get_setting('RESTRICT_PLUGIN_ACCESS')

FORM_ELEMENT_PLUGINS_MODULE_NAME = \
    get_setting('FORM_ELEMENT_PLUGINS_MODULE_NAME')

FORM_HANDLER_PLUGINS_MODULE_NAME = \
    get_setting('FORM_HANDLER_PLUGINS_MODULE_NAME')

FORM_IMPORTER_PLUGINS_MODULE_NAME = \
    get_setting('FORM_IMPORTER_PLUGINS_MODULE_NAME')

FORM_CALLBACKS_MODULE_NAME = get_setting('FORM_CALLBACKS_MODULE_NAME')

THEMES_MODULE_NAME = get_setting('THEMES_MODULE_NAME')

DEFAULT_THEME = get_setting('DEFAULT_THEME')

DISPLAY_AUTH_LINK = get_setting('DISPLAY_AUTH_LINK')

GET_PARAM_INITIAL_DATA = get_setting('GET_PARAM_INITIAL_DATA')

if not DEFAULT_THEME:
    raise NoDefaultThemeSet("No default theme set!")

DEBUG = get_setting('DEBUG')

# **************************************************************
# **************************************************************
# ************************ Theme related ***********************
# **************************************************************
# **************************************************************
CUSTOM_THEME_DATA = get_setting('CUSTOM_THEME_DATA')
THEME_FOOTER_TEXT = get_setting('THEME_FOOTER_TEXT')

# **************************************************************
# **************************************************************
# *********************** Plugin related ***********************
# **************************************************************
# **************************************************************
DEFAULT_MAX_LENGTH = get_setting('DEFAULT_MAX_LENGTH')

FORM_HANDLER_PLUGINS_EXECUTION_ORDER = \
    get_setting('FORM_HANDLER_PLUGINS_EXECUTION_ORDER')

FAIL_ON_MISSING_FORM_ELEMENT_PLUGINS = \
    get_setting('FAIL_ON_MISSING_FORM_ELEMENT_PLUGINS')

FAIL_ON_MISSING_FORM_HANDLER_PLUGINS = \
    get_setting('FAIL_ON_MISSING_FORM_HANDLER_PLUGINS')

FAIL_ON_ERRORS_IN_FORM_ELEMENT_PLUGINS = \
    get_setting('FAIL_ON_ERRORS_IN_FORM_ELEMENT_PLUGINS')

FAIL_ON_ERRORS_IN_FORM_HANDLER_PLUGINS = \
    get_setting('FAIL_ON_ERRORS_IN_FORM_HANDLER_PLUGINS')

# **************************************************************
# **************************************************************
# ************************ Tests related ***********************
# **************************************************************
# **************************************************************
WAIT_BETWEEN_TEST_STEPS = get_setting('WAIT_BETWEEN_TEST_STEPS')
WAIT_AT_TEST_END = get_setting('WAIT_AT_TEST_END')
