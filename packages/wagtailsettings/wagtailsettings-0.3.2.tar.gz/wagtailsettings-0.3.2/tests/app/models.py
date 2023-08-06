from django.db import models

from wagtailsettings import BaseSetting, register_setting


@register_setting
class TestSetting(BaseSetting):
    title = models.CharField(max_length=100)
    email = models.EmailField()
