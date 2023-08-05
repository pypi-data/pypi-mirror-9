__title__ = 'fobi.contrib.plugins.form_elements.fields.textarea.fobi_form_elements'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('TextInputPlugin',)

from django.forms.fields import CharField
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _

from fobi.base import FormFieldPlugin, form_element_plugin_registry, get_theme
from fobi.contrib.plugins.form_elements.fields.textarea import UID
from fobi.contrib.plugins.form_elements.fields.textarea.forms import TextareaForm

theme = get_theme(request=None, as_instance=True)

class TextareaPlugin(FormFieldPlugin):
    """
    Char field plugin.
    """
    uid = UID
    name = _("Textarea")
    group = _("Fields")
    form = TextareaForm

    def get_form_field_instances(self):
        """
        Get form field instances.
        """
        widget_attrs = {
            'class': theme.form_element_html_class,
            'placeholder': self.data.placeholder,
        }
        kwargs = {
            'label': self.data.label,
            'help_text': self.data.help_text,
            'initial': self.data.initial,
            'required': self.data.required,
            'widget': Textarea(attrs=widget_attrs)
        }

        return [(self.data.name, CharField, kwargs)]


form_element_plugin_registry.register(TextareaPlugin)
