__title__ = 'fobi.contrib.plugins.form_elements.fields.input.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('InputForm',)

from django import forms
from django.utils.translation import ugettext_lazy as _

try:
    from django.forms.widgets import NumberInput
except ImportError:
    from django.forms.widgets import TextInput
    class NumberInput(TextInput):
        input_type = 'number'

from fobi.base import BaseFormFieldPluginForm, get_theme
from fobi.settings import DEFAULT_MAX_LENGTH
from fobi.contrib.plugins.form_elements.fields.input.constants import (
    FORM_FIELD_TYPE_CHOICES
    )

theme = get_theme(request=None, as_instance=True)

class InputForm(forms.Form, BaseFormFieldPluginForm):
    """
    Form for ``InputPlugin``.
    """
    plugin_data_fields = [
        ("label", ""),
        ("name", ""),
        ("help_text", ""),
        ("initial", ""),
        ("max_length", "255"),
        ("required", False),
        ("placeholder", ""),

        # Additional elements
        ("autocomplete_value", "off"), # Possible values are: on, off
        ("autofocus_value", False), # If set to True, value should be
                                    # "autofocus"
        ("disabled_value", False), # If set to True, value should be "disabled"
        #("formnovalidate_value", ""), # If set to True, value should be
                                      # "formnovalidate"
        ("list_value", ""),
        ("max_value", ""),
        ("min_value", ""),
        ("multiple_value", False), # If set to True, value should be "multiple"
        ("pattern_value", ""),
        ("readonly_value", False), # If set to True, value should be "readonly"
        ("step_value", ""),
        ("type_value", "text"),
    ]

    label = forms.CharField(
        label = _("Label"),
        required = True,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    name = forms.CharField(
        label = _("Name"),
        required = True,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    help_text = forms.CharField(
        label = _("Help text"),
        required = False,
        widget = forms.widgets.Textarea(attrs={'class': theme.form_element_html_class})
        )
    initial = forms.CharField(
        label = _("Initial"),
        required = False,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    max_length = forms.IntegerField(
        label = _("Max length"),
        required = True,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class}),
        initial = DEFAULT_MAX_LENGTH
        )
    required = forms.BooleanField(
        label = _("Required"),
        required = False,
        widget = forms.widgets.CheckboxInput(attrs={'class': theme.form_element_checkbox_html_class})
        )
    placeholder = forms.CharField(
        label = _("Placeholder"),
        required = False,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )

    # Additional elements
    autocomplete_value = forms.BooleanField(
        label = _("Auto-complete (HTML5 autocomplete)"),
        required = False,
        widget = forms.widgets.CheckboxInput(attrs={'class': theme.form_element_checkbox_html_class})
        )
    autofocus_value = forms.BooleanField(
        label = _("Auto-focus (HTML5 autofocus)"),
        required = False,
        widget = forms.widgets.CheckboxInput(attrs={'class': theme.form_element_checkbox_html_class})
        )
    disabled_value = forms.BooleanField(
        label = _("Disabled"),
        required = False,
        widget = forms.widgets.CheckboxInput(attrs={'class': theme.form_element_checkbox_html_class})
        )
    #formnovalidate_value = forms.BooleanField(
    #    label = _("Skip validation (HTML5 formnovalidate)"),
    #    required = False,
    #    widget = forms.widgets.CheckboxInput(attrs={'class': theme.form_element_html_class})
    #    )
    list_value = forms.CharField(
        label = _("List (HTML5 list)"),
        required = False,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    max_value = forms.CharField(
        label = _("Max (HTML5 max)"),
        required = False,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    min_value = forms.CharField(
        label = _("Min (HTML5 min)"),
        required = False,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    multiple_value = forms.BooleanField(
        label = _("Multiple (HTML5 multiple)"),
        required = False,
        widget = forms.widgets.CheckboxInput(attrs={'class': theme.form_element_checkbox_html_class})
        )
    pattern_value = forms.CharField(
        label = _("Pattern (HTML5 pattern)"),
        required = False,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    readonly_value = forms.BooleanField(
        label = _("Read-only (HTML readonly)"),
        required = False,
        widget = forms.widgets.CheckboxInput(attrs={'class': theme.form_element_checkbox_html_class})
        )
    step_value = forms.IntegerField(
        label = _("Step (HTML5 step)"),
        required = False,
        widget = NumberInput(attrs={'class': theme.form_element_html_class})
        )
    type_value = forms.ChoiceField(
        label = _("Type (HTML type)"),
        required = False,
        choices = FORM_FIELD_TYPE_CHOICES,
        widget = forms.widgets.Select(attrs={'class': theme.form_element_html_class})
        )
