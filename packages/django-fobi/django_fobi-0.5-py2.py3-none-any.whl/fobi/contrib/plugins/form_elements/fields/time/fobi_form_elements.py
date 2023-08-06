from __future__ import absolute_import

__title__ = 'fobi.contrib.plugins.form_elements.fields.time.fobi_form_elements'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('TimeInputPlugin',)

from django.forms.fields import TimeField
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _

from fobi.base import FormFieldPlugin, form_element_plugin_registry, get_theme
from fobi.contrib.plugins.form_elements.fields.time import UID
from fobi.contrib.plugins.form_elements.fields.time.forms \
    import TimeInputForm

theme = get_theme(request=None, as_instance=True)

class TimeInputPlugin(FormFieldPlugin):
    """
    Time field plugin.
    """
    uid = UID
    name = _("Time")
    group = _("Fields")
    form = TimeInputForm

    def get_form_field_instances(self):
        """
        Get form field instances.
        """
        widget_attrs = {
            'class': theme.form_element_html_class,
            'type': 'time',
        }

        kwargs = {
            'label': self.data.label,
            'help_text': self.data.help_text,
            'initial': self.data.initial,
            #'input_formats': self.data.input_formats,
            'required': self.data.required,
            'widget': TextInput(attrs=widget_attrs),
        }
        #if self.data.input_formats:
        #    kwargs['input_formats'] = self.data.input_formats

        return [(self.data.name, TimeField, kwargs)]

    def submit_plugin_form_data(self, form_entry, request, form):
        """
        Submit plugin form data/process.

        :param fobi.models.FormEntry form_entry: Instance of
            ``fobi.models.FormEntry``.
        :param django.http.HttpRequest request:
        :param django.forms.Form form:
        """
        # In case if we should submit value as is, we don't return anything.
        # In other cases, we proceed further.

        # Get the object
        value = form.cleaned_data.get(self.data.name, None)
        try:
            value = value.strftime("%H:%M:%S")
        except Exception as err:
            pass

        # Overwrite ``cleaned_data`` of the ``form`` with object qualifier.
        form.cleaned_data[self.data.name] = value

        return form


form_element_plugin_registry.register(TimeInputPlugin)
