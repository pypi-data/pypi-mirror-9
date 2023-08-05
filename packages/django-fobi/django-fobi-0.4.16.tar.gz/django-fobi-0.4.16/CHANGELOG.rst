Release history and notes
=====================================
`Sequence based identifiers
<http://en.wikipedia.org/wiki/Software_versioning#Sequence-based_identifiers>`_
are used for versioning (schema follows below):

.. code-block:: none

    major.minor[.revision]

- It's always safe to upgrade within the same minor version (for example, from
  0.3 to 0.3.4).
- Minor version changes might be backwards incompatible. Read the
  release notes carefully before upgrading (for example, when upgrading from
  0.3.4 to 0.4).
- All backwards incompatible changes are mentioned in this document.

0.4.16
-------------------------------------
2015-02-10

- A new theme ``djangocms_admin_style_theme`` added.
- Making ``fobi.fields.NoneField`` always valid.
- Initial work on Django 1.8 and 1.9 support.
- Minor fixes.

0.4.15
-------------------------------------
2015-01-27

- Fix the "large" checkboxes in edit mode - now shown small as they should be.

0.4.14
-------------------------------------
2015-01-26

- German translations added.

0.4.13
-------------------------------------
2015-01-15

- Remove an `ipdb` statement from base integration processor
  `fobi.integration.processors.IntegrationProcessor`.
- Added information in the docs about FeinCMS demo part on heroku demo.
- Make sure values of form elements declared not to have a value (``has_value``
  property is set to False) aren't being saved in the ``db_store`` plugin.
- Remove redundant static assets (package size decreased).

0.4.12
-------------------------------------
2015-01-14

- Fix empty options appearing in the Select-like plugins and unified the
  processing of the raw choices data.
- Update the `vishap` package requirement to latest stable 0.1.3.
- Support for wheel packages.

0.4.11
-------------------------------------
2012-12-29

- Styling fixes in the ``radio`` button field of the ``bootstrap3`` theme.
- Fixed ``db_store`` issue with CSV/XLS export failing on Django 1.7.

0.4.10
-------------------------------------
2012-12-28

- Minor fixes in FeinCMS integration app.

0.4.9
-------------------------------------
2012-12-28

- Third party app integration (at the moment, FeinCMS, DjangoCMS, Mezzanine)
  had been generalised and unified.
- Mention the Heroku live demo in the docs.
- Minor CSS fixes in the ``simple`` theme.

0.4.8
-------------------------------------
2012-12-25

- More verbose debugging.

0.4.7
-------------------------------------
2012-12-24

- Temporary left out the "cloneable" column from the dashboard templates.
- Fixed broken imports in CAPTCHA plugin.
- Fixed broken imports in ReCAPTCHA plugin.

0.4.6
-------------------------------------
2012-12-23

- Updated requirements for the ``vishap`` package to avoid the ``six`` version
  conflicts.
- Minor documentation fixes.

0.4.5
-------------------------------------
2012-12-17

- ReCAPTCHA field added.
- Mezzanine integration app added.
- Remove redundant dependencies (django-tinymce).
- Minor improvements of the discover module.

0.4.4
-------------------------------------
2014-12-06

- Documentation improvements.
- Updated Dutch and Russian translations.
- Minor fixes related to lazy translations.

0.4.3
-------------------------------------
2014-12-05

- Make sure values of form elements declared not to have a value (``has_value``
  property is set to False) aren't being saved in the ``db_store`` plugin.
- Apply that to the ``honeypot`` and ``captcha`` plugins.

0.4.2
-------------------------------------
2014-12-04

- Helper script (management command) in order to migrate django-fobi==0.3.* 
  data to django-fobi==0.4.* data (caused by renaming the ``birthday`` field 
  to ``date_drop_down`` - see the release notes of 0.4 below). Follow the steps
  precisely in order to painlessly upgrade your django-fobi==0.3.* to
  django-fobi==0.4.*:

  1. Install django-fobi>=0.4.2::

         pip install django-fobi>=0.4.2

  2. In your settings change the::

         'fobi.contrib.plugins.form_elements.fields.birthday'
         
     to::

         'fobi.contrib.plugins.form_elements.fields.date_drop_down'

  3. Run the ``migrate_03_to_04`` management command::

         ./manage.py migrate_03_to_04

0.4.1
-------------------------------------
2014-12-04

- Fixes in Foundation5 and Simple themes related to the changes in error
  validation/handling of hidden fields.

0.4
-------------------------------------
2014-12-03

Note, that this release contains minor backwards incompatible changes. The
changes may affect your existing forms and data. Read the notes below
carefully (UPDATE 2014-12-04: the django-fobi==0.4.2 contains a management 
command which makes the necessary changes in the database for safe upgrade).

- The ``captcha`` field has been moved from 
  ``fobi.contrib.plugins.form_elements.fields.captcha`` to
  ``fobi.contrib.plugins.form_elements.security.captcha``. Make sure to update
  the package paths in ``INSTALLED_APPS`` of your projects' settings module
  (settings.py) when upgrading to this version.
- The ``honeypot`` field has been added.
- The ``birthday`` field has been renamed to ``date_drop_down`` (A real
  ``birthday`` field is still to come in later releases). The change causes
  backwards incompatibility issues if you have used that ``birthday`` field.
  If you haven't - you have nothing to worry. If you have been using it,
  grab the 0.3.4 version, copy the
  ``fobi.contrib.plugins.form_elements.fields.date_drop_down`` package to
  your project apps, make necessary path changes and update the package paths
  in ``INSTALLED_APPS`` settings module (settings.py) before upgrading to this
  version. Then, in Django admin management interface, replace all the
  occurances of ``Birthday`` field with ``Date drop down`` field.
- Better error validation/handling of hidden fields. A new form snippet 
  template added for displaying the non-field and hidden fields errors. The new
  template makes a part of a standard theme as an attribute
  ``form_non_field_and_hidden_errors_snippet_template``.
- Minor fixes in generic templates.
- An additional property ``is_hidden`` added to the hidden form elements. Those
  form elements would be getting a default TextInput widget in the edit mode
  instead of the widget they come from by default. It's possible to provide an
  alternative widget for the edit mode as well. Default value of the
  ``is_hidden`` is set to False.

0.3.4
-------------------------------------
2014-11-23

- New settings ``FOBI_FAIL_ON_ERRORS_IN_FORM_ELEMENT_PLUGINS`` and
  ``FOBI_FAIL_ON_ERRORS_IN_FORM_HANDLER_PLUGINS`` introduced. They do as 
  their name tells. Default value for both is False.
- Fixed exceptions raised when unicode characters were used as form names.
- Fixed exceptions raised when unicode characters were used as field labels.
- Fixes in the `db_store` and `mail` plugins related to usage of unicode
  characters.

0.3.3
-------------------------------------
2014-11-22

- Clean up the setup. Remove redundant dependencies.
- Documentation improvements.

0.3.2
-------------------------------------
2014-11-20

- DjangoCMS integration app made compatible with DjangoCMS 2.4.3.

0.3.1
-------------------------------------
2014-11-19

- DjangoCMS integration app.

0.3
-------------------------------------
2014-11-09

Note, that this release contains minor backwards incompatible changes. The
changes do not anyhow affect your existing forms or data. The only thing you
need to do is update the app paths in the ``settings`` module of your project.

- Minor core improvements related to the themeing of the form handler plugins.
- Several presentational form element plugins have been renamed.
  The ``fobi.contrib.plugins.form_elements.content.image`` plugin has been
  renamed to ``fobi.contrib.plugins.form_elements.content.content_image``.
  The ``fobi.contrib.plugins.form_elements.content.text`` plugin has been
  renamed to ``fobi.contrib.plugins.form_elements.content.content_text``.
  The ``fobi.contrib.plugins.form_elements.content.video`` plugin has been
  renamed to ``fobi.contrib.plugins.form_elements.content.content_video``.
  If you have used any of the above mentioned plugins, make sure to update 
  the app paths in the ``settings`` module of your project.
- The ``fobi.contrib.plugins.form_elements.content.dummy`` plugin has been moved
  to ``fobi.contrib.plugins.form_elements.test.dummy`` location. If you have
  used it, make sure to update the its' path in the ``settings`` module of
  your project.
- Added readme to the following content form element plugins: ``dummy``,
  ``content_image``, ``content_text`` and ``content_video``.
- Added ``foundation5`` and ``simple`` theme widgets for ``db_store`` plugin.
- If you have been overriding the defaults of the ``db_store`` plugin, change
  the prefix from ``FOBI_PLUGIN_DB_EXPORT_`` to ``FOBI_PLUGIN_DB_STORE_``. For
  example,  ``FOBI_PLUGIN_DB_EXPORT_CSV_DELIMITER`` should become
  ``FOBI_PLUGIN_DB_STORE_CSV_DELIMITER``.
- Mentioning the ``fobi_find_broken_entries`` management command in the
  documentation, as well as improving the management command itself (more
  verbose output).
- Birthday field added.

0.2.1
-------------------------------------
2014-11-06

- Minor improvements of the ``db_store`` plugin.
- Minor improvements of the ``simple`` theme. Make sure that custom
  form handler actions are properly shown in the form handlers list.
- Make it possible to fail silently on missing form element or form
  handler plugins by setting the respected values to False: 
  ``FOBI_FAIL_ON_MISSING_FORM_ELEMENT_PLUGINS``,
  ``FOBI_FAIL_ON_MISSING_FORM_HANDLER_PLUGINS``. Otherwise an appropriate
  exception is raised.

0.2
-------------------------------------
2014-11-05

Note, that this release contains minor backwards incompatible changes.

- Minor (backwards incompatible) changes in the form handler plugin API. 
  From now on both ``custom_actions`` and ``get_custom_actions`` methods
  accept ``form_entry`` (obligatory) and ``request`` (optional) arguments. If
  you have written your own or have changed existing form handler plugins
  with use of one of the above mentioned methods, append those arguments to
  the method declarations when upgrading to this version. If you haven't
  written your own or changed existing form handler plugins, you may just 
  upgrade to this version.
- Added data export features to the ``db_store`` plugin.
- Minor fixes in ``db_store`` plugin.
- Added missing documentation for the ``feincms_integration`` app.
- Updated translations for Dutch and Russian.

0.1.6
-------------------------------------
2014-10-25

- Minor improvements in the theming API. From now on the
  ``view_embed_form_entry_ajax_template`` template would be used
  when integrating the form rendering from other products (for example,
  a CMS page, which has a widget which references the form object. If
  that property is left empty, the ``view_form_entry_ajax_template``
  is used. For a success page the ``embed_form_entry_submitted_ajax_template``
  template would be used.
- Functional improvements of the FeinCMS integration (the widget). If you
  have used the FeinCMS widget of earlier versions, you likely want to update 
  to this one. From now on you can select a custom form title and the button
  text, as well as provide custom success page title and the success  message;
  additionally, it has been made possible to hide the form- or success-page-
  titles.

0.1.5
-------------------------------------
2014-10-23

- Minor fixes in the ``Integer`` form element plugin.
- Minor fixes in the ``Input`` form element plugin.
- Minor fixes in themes (disable HTML5 form validation in edit mode).
- Minor documentation improvements.

0.1.4
-------------------------------------
2014-10-22

- Minor core improvements.
- Django 1.5 support improvements.
- Django 1.7 support improvements.
- Added ``Captcha`` form element plugin.
- Added highly-customisable ``Input`` form element plugin - a custom input field
  with support for almost any ever existing HTML attribute.
- Documentation improvements.

0.1.3
-------------------------------------
2014-10-13

- Django 1.7 support.
- Add HTML5 "placeholder" field attribute support.

0.1.2
-------------------------------------
2014-10-11

- Simple theme fixes: Fix for making the theme work in Django 1.5.

0.1.1
-------------------------------------
2014-10-11

- Bootstrap 3 theme fixes: When tab pane has no or little content so
  that the height of the dropdown menu exceeds the height of the tab pane
  content the dropdown menu now becomes scrollable (vertically).

0.1
-------------------------------------
2014-10-11

- Initial release.
