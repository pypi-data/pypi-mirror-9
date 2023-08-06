__title__ = 'fobi.contrib.plugins.form_elements.content.content_text.fobi_form_elements'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014-2015 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('ContentTextPlugin',)

from uuid import uuid4

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str

from fobi.base import FormElementPlugin, form_element_plugin_registry
from fobi.fields import NoneField
from fobi.contrib.plugins.form_elements.content.content_text import UID
from fobi.contrib.plugins.form_elements.content.content_text.forms \
    import ContentTextForm

class ContentTextPlugin(FormElementPlugin):
    """
    Content text plugin.
    """
    uid = UID
    name = _("Content text")
    group = _("Content")
    form = ContentTextForm

    def post_processor(self):
        """
        Always the same.
        """
        self.data.name = "{0}_{1}".format(self.uid, uuid4())

    def get_form_field_instances(self):
        """
        Get form field instances.
        """
        kwargs = {
            'initial': "<p>{0}</p>".format(smart_str(self.data.text)),
            'required': False,
            'label': '',
        }

        form_field_instances = []

        form_field_instances.append((self.data.name, NoneField, kwargs))
        return form_field_instances


form_element_plugin_registry.register(ContentTextPlugin)
