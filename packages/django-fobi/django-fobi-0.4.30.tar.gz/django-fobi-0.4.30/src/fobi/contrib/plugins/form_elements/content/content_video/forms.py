__title__ = 'fobi.contrib.plugins.form_elements.content.content_video.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2014 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('ContentVideoForm',)

from django import forms
from django.utils.translation import ugettext_lazy as _

from fobi.base import BasePluginForm, get_theme
from fobi.contrib.plugins.form_elements.content.content_video.settings import (
    DEFAULT_SIZE, SIZES
    )

theme = get_theme(request=None, as_instance=True)

class ContentVideoForm(forms.Form, BasePluginForm):
    """
    Form for ``ContentVideoPlugin``.
    """
    plugin_data_fields = [
        ("title", ""),
        ("url", ""),
        ("size", DEFAULT_SIZE),
    ]

    title = forms.CharField(
        label = _("Title"),
        required = True,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    url = forms.CharField(
        label = _("URL"),
        required = True,
        widget = forms.widgets.TextInput(attrs={'class': theme.form_element_html_class})
        )
    size = forms.ChoiceField(
        label = _("Size"),
        required = False,
        initial = DEFAULT_SIZE,
        choices = SIZES,
        widget = forms.widgets.Select(attrs={'class': theme.form_element_html_class})
        )
