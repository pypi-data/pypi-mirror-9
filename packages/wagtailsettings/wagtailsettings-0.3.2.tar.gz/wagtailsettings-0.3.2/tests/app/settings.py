DEBUG = True

INSTALLED_APPS = [
    'wagtailsettings',
    'tests.app',

    'wagtail.wagtailcore',
    'wagtail.wagtailadmin',
    'wagtail.wagtailusers',
    'wagtail.wagtailsites',

    'taggit',
    'compressor',
    'modelcluster',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sql',
    }
}

SECRET_KEY = 'Not very secret'

ROOT_URLCONF = 'tests.app.urls'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
]

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
    'wagtailsettings.context_processors.settings',
)

WAGTAIL_SITE_NAME = 'Wagtail settings test app'

import os
STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = '/static/'
