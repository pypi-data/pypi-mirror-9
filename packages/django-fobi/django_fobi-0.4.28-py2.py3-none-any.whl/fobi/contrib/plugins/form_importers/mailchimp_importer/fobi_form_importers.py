from django.utils.translation import ugettext_lazy as _

from fobi.form_importers import BaseFormImporter, form_importer_plugin_registry
from fobi.contrib.plugins.form_elements import fields

#mailchimp_fobi_mapping =

class MailChimpFormImporter(BaseFormImporter):
    """
    MailChimp data importer.
    """
    uid = 'mailchimp'
    name = _("MailChimp")

    # field_type (MailChimp): uid (Fobi)
    fields_mapping = {
        # Implemented
        'email': fields.email.UID,
        'text': fields.text.UID,
        'number': fields.integer.UID,
        'dropdown': fields.select.UID,
        'date': fields.date.UID,
        'url': fields.url.UID,

        # Transformed into something else
        'address': fields.text.UID,
        'zip': fields.text.UID,
        'phone': fields.text.UID,

        # Unsure of what to do
        #'imageurl': '???',

        # Not implemented yet
        #'radio': '???',
        #
        #'birthday': '???',
    }

    # Django standard: remote
    field_properties_mapping = {
        'label': 'name',
        'name': 'tag',
        'help_text': 'helptext',
        'initial': 'default',
        'required': 'req',
        'choices': 'choices',
        
    }

    field_type_prop_name = 'field_type'
    position_prop_name = 'order'

    def extract_field_properties(self, field_data):
        """
        Handle choices differently as we know what the mailchimp
        format is.
        """
        field_properties = {}
        for prop, val in self.field_properties_mapping.items():
            if val in field_data:
                if 'choices' == val:
                    field_properties[prop] = "\n".join(field_data[val])
                else:
                    field_properties[prop] = field_data[val]
        return field_properties

form_importer_plugin_registry.register(MailChimpFormImporter)
