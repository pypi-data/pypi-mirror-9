from django.conf import settings
from django.contrib.auth import get_user_model

from fobi.contrib.plugins.form_importers.mailchimp_importer.fobi_form_importers \
    import MailChimpFormImporter


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

test_form_data = [
    {u'default': u'',
     u'field_type': u'email',
     u'helptext': u'',
     u'id': 0,
     u'name': u'Email Address',
     u'order': u'1',
     u'public': True,
     u'req': True,
     u'show': True,
     u'size': u'25',
     u'tag': u'EMAIL'},
    {u'default': u'',
     u'field_type': u'text',
     u'helptext': u'',
     u'id': 1,
     u'name': u'First Name',
     u'order': u'2',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'FNAME'},
    {u'default': u'',
     u'field_type': u'text',
     u'helptext': u'',
     u'id': 2,
     u'name': u'Last Name',
     u'order': u'3',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'LNAME'},
    {u'default': u'',
     u'field_type': u'text',
     u'helptext': u'',
     u'id': 3,
     u'name': u'Organisation',
     u'order': u'4',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'ORG'},
    {u'default': u'Type Text Default Value',
     u'field_type': u'text',
     u'helptext': u'Type Text Help Text',
     u'id': 4,
     u'name': u'type_text',
     u'order': u'5',
     u'public': True,
     u'req': True,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_TEXT'},
    {u'default': u'1',
     u'field_type': u'number',
     u'helptext': u'Type Number Help Text',
     u'id': 5,
     u'name': u'type_number',
     u'order': u'6',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_NUMBE'},
    {u'choices': [u'First Choice', u'Second Choice', u'Third Choice'],
     u'default': u'Second Choice',
     u'field_type': u'radio',
     u'helptext': u'Type Radio Buttons Help Text',
     u'id': 6,
     u'name': u'type_radio_buttons',
     u'order': u'7',
     u'public': True,
     u'req': True,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_RADIO'},
    {u'choices': [u'First Choice', u'Second Choice', u'Third Choice'],
     u'default': u'Third Choice',
     u'field_type': u'dropdown',
     u'helptext': u'Drop Down Help Text',
     u'id': 7,
     u'name': u'type_drop_down',
     u'order': u'9',
     u'public': True,
     u'req': True,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_DROPD'},
    {u'dateformat': u'MM/DD/YYYY',
     u'default': u'',
     u'field_type': u'date',
     u'helptext': u'Type Date Help Text',
     u'id': 8,
     u'name': u'type_date',
     u'order': u'10',
     u'public': True,
     u'req': True,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_DATE'},
    {u'dateformat': u'MM/DD',
     u'default': u'',
     u'field_type': u'birthday',
     u'helptext': u'Type Birthday Help Text',
     u'id': 9,
     u'name': u'type_birthday',
     u'order': u'11',
     u'public': True,
     u'req': True,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_BIRTH'},
    {u'default': u'',
     u'defaultcountry': u'109',
     u'defaultcountry_cc': u'NL',
     u'defaultcountry_name': u'Netherlands',
     u'field_type': u'address',
     u'helptext': u'Type Address Help Text',
     u'id': 10,
     u'name': u'type_address',
     u'order': u'12',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_ADDRE'},
    {u'default': u'',
     u'field_type': u'zip',
     u'helptext': u'Type Zip Code Help Text',
     u'id': 11,
     u'name': u'type_zip_code',
     u'order': u'13',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_ZIP_C'},
    {u'default': u'',
     u'field_type': u'phone',
     u'helptext': u'Type Phone Help Text',
     u'id': 12,
     u'name': u'type_phone',
     u'order': u'14',
     u'phoneformat': u'none',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_PHONE'},
    {u'default': u'',
     u'field_type': u'url',
     u'helptext': u'Type Website Help Text',
     u'id': 13,
     u'name': u'type_website',
     u'order': u'15',
     u'public': True,
     u'req': True,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_WEBSI'},
    {u'default': u'',
     u'field_type': u'imageurl',
     u'helptext': u'Type Image Help Text',
     u'id': 14,
     u'name': u'type_image',
     u'order': u'16',
     u'public': True,
     u'req': False,
     u'show': True,
     u'size': u'25',
     u'tag': u'TYPE_IMAGE'}
]

def do():
    User = get_user_model()
    user = User.objects.get(username='test_admin')

    form_properties = {'name': 'Test mailchimp form', 'user': user}

    importer = MailChimpFormImporter(form_properties, test_form_data)

    importer.import_data()
