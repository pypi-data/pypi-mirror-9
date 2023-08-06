from django.template import Library
from wagtailsettings.context_processors import SettingsProxy

register = Library()


@register.simple_tag(takes_context=True)
def get_settings(context):
    context['settings'] = SettingsProxy()
    return ''
