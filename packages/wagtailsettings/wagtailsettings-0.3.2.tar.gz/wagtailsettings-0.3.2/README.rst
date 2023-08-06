===============
wagtailsettings
===============

A plugin for Wagtail that adds developer-defined settings to the admin.

Installing
==========

Install using pip::

    pip install wagtailsettings

It is compatible with Wagtail 1.0 and upwards.

Add it to your ``INSTALLED_APPS``:

.. code:: python

    INSTALLED_APPS += [
        'wagtailsettings',
    ]


Using
=====

Create a model that inherits from ``BaseSetting``,
and register it using the ``register_setting`` decorator:

.. code:: python

    from wagtailsettings import BaseSetting, register_setting

    @register_setting
    class SocialMediaSettings(BaseSetting):
        facebook = models.URLField(
            help_text='Your Facebook page URL')
        instagram = models.CharField(
            max_length=255, help_text='Your Instagram username, without the @')
        trip_advisor = models.URLField(
            help_text='Your Trip Advisor page URL')
        youtube = models.URLField(
            help_text='Your YouTube channel or user account URL')


A 'Social media settings' link will appear in the Wagtail admin 'Settings' menu.

You can change the label used in the menu by changing the
`verbose_name <https://docs.djangoproject.com/en/dev/ref/models/options/#verbose-name>`_
of your model.

You can add an icon to the menu
by passing an 'icon' argument to the ``register_setting`` decorator:

.. code:: python

    @register_setting(icon='icon-placeholder')
    class SocialMediaSettings(BaseSetting):
        # ...

For a list of all available icons, please see the Wagtail style guide.

Using in Python
---------------

If access to a setting is required in the code,
the ``BaseSetting.for_site`` method will retrieve the setting for the supplied site:

.. code:: python

    def view(request):
        social_media_settings = SocialMediaSettings.for_site(request.site)
        ...

Using in Templates
------------------

Add the ``request`` and ``wagtailsettings`` context processors to your settings:

.. code:: python

    from django.conf import global_settings
    TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
        'wagtailsettings.context_processors.settings',
    )

Then access the settings through ``settings``:

.. code:: html+django

    {{ settings.app_label.SocialMediaSettings.instagram }}

If you are not in a RequestContext, then context processors will not have run,
and the ``settings`` variable will not be availble. To get the ``settings``,
use the provided template tags:

.. code:: html+django

    {% load wagtailsettings_tags %}
    {% get_settings %}
    {{ settings.app_label.SocialMediaSettings.instagram }}

.. note:: You can not reliably get the correct settings instance for the
    current site from this template tag, as the request object is not
    available. This is only relevant for multisite instances of Wagtail though,
    so most developers will not have to worry.
