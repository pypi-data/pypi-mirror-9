from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase

from wagtail.tests.utils import WagtailTestUtils

from wagtailsettings import BaseSetting
from wagtailsettings.registry import Registry

class TestRegister(TestCase, WagtailTestUtils):
    def setUp(self):
        self.registry = Registry()
        self.login()

    def test_register(self):
        @self.registry.register
        class Setting(BaseSetting):
            pass

        self.assertIn(Setting, self.registry.models)

    def test_icon(self):
        admin = self.client.get(reverse('wagtailadmin_home'))
        self.assertContains(admin, 'icon icon-tag')