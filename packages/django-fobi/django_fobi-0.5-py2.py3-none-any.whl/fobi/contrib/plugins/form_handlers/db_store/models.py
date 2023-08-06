__title__ = 'fobi.contrib.plugins.form_handlers.db_store.models'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014-2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('SavedFormDataEntry',)

#import json

import simplejson as json

from six import string_types

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.db import models

# ****************************************************************************
# **************** Safe User import for Django > 1.5, < 1.8 ******************
# ****************************************************************************
AUTH_USER_MODEL = settings.AUTH_USER_MODEL

# Note, that this may cause circular imports - thus the ``get_user_model``
# should be moved elsewhere (be used on the function/method level). For
# now leave commented and solve in future. Possible use the DjangoCMS solution
# https://github.com/divio/django-cms/blob/develop/cms/models/permissionmodels.py#L18

# Sanity checks.
#user = User()
#
#if not hasattr(user, 'username'):
#    from fobi.exceptions import ImproperlyConfigured
#    raise ImproperlyConfigured("Your custom user model ({0}.{1}) doesn't "
#                               "have ``username`` property, while "
#                               "``django-fobi`` relies on its' presence"
#                               ".".format(user._meta.app_label, user._meta.object_name))

# ****************************************************************************
# ****************************************************************************
# ****************************************************************************

from fobi.helpers import two_dicts_to_string

class SavedFormDataEntry(models.Model):
    """
    Saved form data.
    """
    form_entry = models.ForeignKey('fobi.FormEntry', verbose_name=_("Form"),
                                   null=True, blank=True)
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_("User"),
                             null=True, blank=True)
    form_data_headers = models.TextField(_("Form data headers"), null=True,
                                         blank=True)
    saved_data = models.TextField(_("Plugin data"), null=True, blank=True)
    created = models.DateTimeField(_("Date created"), auto_now_add=True)

    class Meta:
        abstract = False
        verbose_name = _("Saved form data entry")
        verbose_name_plural = _("Saved form data entries")
        db_table = 'db_store_savedformdataentry'

    def __unicode__(self):
        return "Saved form data entry from {0}".format(self.created)

    def formatted_saved_data(self):
        """
        Shows the formatted saved data records.

        :return string:
        """
        headers = json.loads(self.form_data_headers)
        data = json.loads(self.saved_data)
        for key, value in data.items():
            if isinstance(value, string_types) and \
               (value.startswith(settings.MEDIA_URL) or \
                value.startswith('http://') or value.startswith('https://')):

                data[key] = '<a href="{value}">{value}</a>'.format(value=value)

        return two_dicts_to_string(headers, data)
    formatted_saved_data.allow_tags = True
    formatted_saved_data.short_description = _("Saved data")
