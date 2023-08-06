===============
wagtailsettings
===============

A plugin for Wagtail that provides add developer-defined settings to the admin.

Installing
==========

Install using pip::

    pip install wagtailsettings

It works with Wagtail 0.5 and upwards.

Add it to your ``INSTALLED_APPS``:

.. code:: python

    INSTALLED_APPS += [
        'wagtailnews',
    ]


Using
=====

Create a model that inherits from ``BaseSetting``,
and register it using the ``register_setting`` decorator:

.. code:: python

    from wagtailnews.models import BaseSetting, register_setting

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


A 'Settings' link will appear in the Wagtail admin,
with links to each of the settings models defined.

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

Add the ``request`` and ``wagtailnews`` context processors to your settings:

.. code:: python

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
