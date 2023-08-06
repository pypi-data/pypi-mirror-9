__title__ = 'fobi.contrib.plugins.form_elements.fields.select.fobi_form_elements'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('SelectInputPlugin',)

from django.forms.fields import ChoiceField
from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _

from fobi.base import FormFieldPlugin, form_element_plugin_registry, get_theme
from fobi.constants import (
    SUBMIT_VALUE_AS_VAL, SUBMIT_VALUE_AS_REPR
    )
from fobi.helpers import get_select_field_choices, safe_text
from fobi.contrib.plugins.form_elements.fields.select import UID
from fobi.contrib.plugins.form_elements.fields.select.forms import (
    SelectInputForm
    )
from fobi.contrib.plugins.form_elements.fields.select.settings import (
    SUBMIT_VALUE_AS
    )

theme = get_theme(request=None, as_instance=True)

class SelectInputPlugin(FormFieldPlugin):
    """
    Select field plugin.
    """
    uid = UID
    name = _("Select")
    group = _("Fields")
    form = SelectInputForm

    def get_form_field_instances(self):
        """
        Get form field instances.
        """
        choices = get_select_field_choices(self.data.choices)

        kwargs = {
            'label': self.data.label,
            'help_text': self.data.help_text,
            'initial': self.data.initial,
            'required': self.data.required,
            'choices': choices,
            'widget': Select(attrs={'class': theme.form_element_html_class}),
        }

        return [(self.data.name, ChoiceField, kwargs)]

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
        if SUBMIT_VALUE_AS != SUBMIT_VALUE_AS_VAL:
            # Get the object
            value = form.cleaned_data.get(self.data.name, None)

            # Get choices
            choices = dict(get_select_field_choices(self.data.choices))

            if value in choices:
                # Handle the submitted form value

                label = safe_text(choices.get(value))

                # Should be returned as repr
                if SUBMIT_VALUE_AS == SUBMIT_VALUE_AS_REPR:
                    value = label
                # Should be returned as mix
                else:
                    value = "{0} ({1})".format(label, value)

                # Overwrite ``cleaned_data`` of the ``form`` with object
                # qualifier.
                form.cleaned_data[self.data.name] = value

                # It's critically important to return the ``form`` with updated
                # ``cleaned_data``
                return form


form_element_plugin_registry.register(SelectInputPlugin)
