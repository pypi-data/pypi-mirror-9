from django.test import TestCase, modify_settings
from django.template import Template, Context, RequestContext

from wagtail.tests.utils import WagtailTestUtils
from tests.app.models import TestSetting
from wagtail.wagtailcore.models import Site


class TemplateTestCase(TestCase, WagtailTestUtils):
    def setUp(self):
        default_site = Site.objects.get(is_default_site=True)

        self.test_setting = TestSetting.objects.create(
            title='Site title',
            email='initial@example.com',
            site=default_site)


class TestContextProcessor(TemplateTestCase):

    def render(self, string, context=None):
        template = Template(string)
        context = RequestContext(self.client.get('/test/'), context)
        return template.render(context)

    def test_accessing_setting(self):
        self.assertEqual(
            self.render('{{ settings.app.TestSetting.title }}'),
            self.test_setting.title)

    def test_model_case_insensitive(self):
        self.assertEqual(
            self.render('{{ settings.app.testsetting.title }}'),
            self.test_setting.title)
        self.assertEqual(
            self.render('{{ settings.app.TESTSETTING.title }}'),
            self.test_setting.title)
        self.assertEqual(
            self.render('{{ settings.app.TestSetting.title }}'),
            self.test_setting.title)
        self.assertEqual(
            self.render('{{ settings.app.tEstsEttIng.title }}'),
            self.test_setting.title)


@modify_settings(TEMPLATE_CONTEXT_PROCESSORS={
    'remove': 'wagtailsettings.context_processors.settings',
})
class TestTemplateTag(TemplateTestCase):

    def render(self, string, context=None):
        template = Template(string)
        context = Context(context)
        return template.render(context)

    def test_no_context_processor(self):
        self.assertEqual(
            self.render('{{ settings.app.TestSetting.title }}'),
            '')

    def test_accessing_setting(self):
        preamble = '{% load wagtailsettings_tags %}{% get_settings %}'
        self.assertEqual(
            self.render(preamble + '{{ settings.app.TestSetting.title }}'),
            self.test_setting.title)
