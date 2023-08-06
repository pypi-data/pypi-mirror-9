#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import os
import sys

gettext = lambda s: s
"""
Django settings for Pegasus project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, 'extensions'))
sys.path.append(os.path.join(BASE_DIR, 'plugins'))
sys.path.append(os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h%v89*ik-=#+$nn+#%^(n(r+6bhs=r+q)a2o%n&k&doup&tce('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition


ROOT_URLCONF = 'pegasus.urls'

WSGI_APPLICATION = 'pegasus.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATIC_FILES_LOADER = 'django.contrib.staticfiles.templatetags.staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


SITE_ID = 2

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.i18n',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.csrf',
    'django.core.context_processors.tz',
    'sekizai.context_processors.sekizai',
    'django.core.context_processors.static',
    'cms.context_processors.cms_settings'
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'pegasus', 'templates'),
)

INSTALLED_APPS = (

    # Preloads
    'precompressed',

    # Django Apps
    'djangocms_admin_style',
    'djangocms_text_ckeditor',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',

    # Django-CMS Apps
    'cms',
    'mptt',
    'menus',
    #'south',
    'sekizai',
    'djangocms_style',
    'djangocms_column',
    'djangocms_file',
    'djangocms_flash',
    'djangocms_googlemap',
    'djangocms_inherit',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_teaser',
    'djangocms_video',
    #'cmsplugin_soundcloud',
    'reversion',

    # Custom Django-CMS Apps
    #'pegasus',
    'content',
    'authors',
    'search',
    'files',

    # Custom Django-CMS Extensions
    'content_list',
    'tombstones',
    'left_nav',
    'page_extras',

    # Custom Django-CMS Plugins
    'utils',
    'tombstone',
    'four_up',
    'masthead',
    'carousel',

    # Third-Party Applications
    'django_extensions',
    'taggit',
    'haystack',
    'sorl.thumbnail',
    #'standard_form', # dependency for aldryn_search
    #'spurl',         # dependency for aldryn_search
    #'aldryn_search',
    'genericadmin',
)

SOUTH_MIGRATION_MODULES = {
    'taggit': 'taggit.south_migrations',
}

MIGRATION_MODULES = {
    'cms': 'cms.migrations_django',
    'menus': 'menus.migrations_django',
    'djangocms_column': 'djangocms_column.migrations_django',
    'djangocms_file': 'djangocms_file.migrations_django',
    'djangocms_flash': 'djangocms_flash.migrations_django',
    'djangocms_googlemap': 'djangocms_googlemap.migrations_django',
    'djangocms_inherit': 'djangocms_inherit.migrations_django',
    'djangocms_link': 'djangocms_link.migrations_django',
    'djangocms_picture': 'djangocms_picture.migrations_django',
    'djangocms_snippet': 'djangocms_snippet.migrations_django',
    'djangocms_style': 'djangocms_style.migrations_django',
    'djangocms_teaser': 'djangocms_teaser.migrations_django',
    'djangocms_video': 'djangocms_video.migrations_django',
    'djangocms_text_ckeditor': 'djangocms_text_ckeditor.migrations_django',
    'carousel': 'carousel.migrations',
    'four_up': 'four_up.migrations_django',
    'masthead': 'masthead.migrations',
    'tombstone': 'tombstone.migrations',
}

LANGUAGES = (
    ## Customize this
    ('en', gettext('en')),
)

CMS_LANGUAGES = {
    ## Customize this
    'default': {
        'public': True,
        'hide_untranslated': False,
        'redirect_on_fallback': True,
    },
    1: [
        {
            'public': True,
            'code': 'en',
            'hide_untranslated': False,
            'name': gettext('en'),
            'redirect_on_fallback': True,
        },
    ],
}

CMS_TEMPLATES = (
    ('pegasus/page.html', 'Page'),
    ('pegasus/pages/home.html', 'Home'),
    ('pegasus/pages/work.html', 'Work'),
    ('pegasus/pages/news.html', 'News'),
    ('pegasus/pages/connect.html', 'Connect'),
    ('pegasus/pages/contact.html', 'Contact'),
    ('pegasus/pages/about.html', 'About'),
    ('pegasus/pages/search.html', 'Search'),
    ('pegasus/pages/team.html', 'People'),
    ('pegasus/pages/donate.html', 'Donate'),
    ('pegasus/pages/email.html', 'Keep Me Informed')
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {
    '4up': {
        'plugins': ['CMSFourUpPlugin'],
    },
    'carousel': {
        'plugins': ['CMSCarouselPlugin'],
    },
    'masthead': {
        'plugins': ['CMSMastheadPlugin'],
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'project.db',
        'HOST': 'localhost',
        'USER': '',
        'PASSWORD': '',
        'PORT': '',
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    }
}
HAYSTACK_ROUTERS = [
    #'aldryn_search.router.LanguageRouter',
    'haystack.routers.DefaultRouter',
]

ALDRYN_SEARCH_LANGUAGE_FROM_ALIAS = lambda alias: alias.split('-')[-1]
ALDRYN_SEARCH_REGISTER_APPHOOK = False # required for extending aldryn_search
ALDRYN_SEARCH_PAGINATION = 10

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pegasus-default',
    },
    'decorated': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {

    },
    'filters': {

    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins',],
            'level': 'ERROR',
            'propagate': False,
        },
        'elasticsearch': {
            'handlers': ['console', 'mail_admins',],
            'level': 'INFO',
        },
        'elasticsearch.trace': {
            'handlers': ['console',],
            'level': 'INFO',
            'propagate': False,
        },
        'search': {
            'handlers': ['console',],
            'level': 'INFO',
        },
        'pegasus': {
            'handlers': ['console', 'mail_admins',],
            'level': 'INFO',
        },
    },
}

TEXT_ADDITIONAL_TAGS = (u'iframe', u'script',)  # they asked for it
TEXT_HTML_SANITIZE = True

CKEDITOR_SETTINGS = {
    'basicEntities': False,
    'entities': False,
}
