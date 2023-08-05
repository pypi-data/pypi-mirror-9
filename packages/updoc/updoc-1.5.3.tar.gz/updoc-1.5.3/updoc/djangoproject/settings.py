# -*- coding: utf-8 -*-
""" Django settings for updoc project. """
from urllib.parse import urlparse

from os.path import join, dirname, abspath
from django.utils.translation import ugettext_lazy as _

from updoc.djangoproject.configuration import ConfigurationParser


__author__ = "flanker"

# read the configuration files

CONFIGURATION = ConfigurationParser()
# compute the path of the updoc.ini file
__config_path_comp = abspath(__file__).split('/')
CONFIG_FILES = [abspath(join(__file__, '..', '..', 'updoc.ini'))]
if 'lib' in __config_path_comp:
    # noinspection PyTypeChecker
    path = '/'.join(__config_path_comp[0:__config_path_comp.index('lib')] + ['etc', 'updoc.ini'])
    CONFIG_FILES.append(abspath(path))
CONFIGURATION.read(CONFIG_FILES)

ROOT_PATH = CONFIGURATION.get('updoc', 'ROOT_PATH', fallback=None)
if not ROOT_PATH:
    ROOT_PATH = abspath(join(dirname(dirname(dirname(__file__))), 'django_data'))
HOST = CONFIGURATION.get('updoc', 'HOST', fallback='http://localhost:8002')
DEBUG = CONFIGURATION.getboolean('updoc', 'DEBUG', fallback=True)
TIME_ZONE = CONFIGURATION.get('updoc', 'TIME_ZONE', fallback='Europe/Paris')
LANGUAGE_CODE = CONFIGURATION.get('updoc', 'LANGUAGE_CODE', fallback='fr-fr')
USE_XSENDFILE = CONFIGURATION.getboolean('updoc', 'USE_XSENDFILE', fallback=False)
FAKE_AUTHENTICATION_USERNAME = CONFIGURATION.get('updoc', 'FAKE_AUTHENTICATION_USERNAME', fallback=None)
PUBLIC_INDEX = CONFIGURATION.getboolean('updoc', 'PUBLIC_INDEX', fallback=True)
PUBLIC_DOCS = CONFIGURATION.getboolean('updoc', 'PUBLIC_DOCS', fallback=True)
PUBLIC_BOOKMARKS = CONFIGURATION.getboolean('updoc', 'PUBLIC_FAVORITES', fallback=True)
PUBLIC_PROXIES = CONFIGURATION.getboolean('updoc', 'PUBLIC_PROXIES', fallback=True)
REMOTE_USER_HEADER = CONFIGURATION.get('updoc', 'REMOTE_USER_HEADER', fallback='REMOTE_USER')
DATABASE_ENGINE = CONFIGURATION.get('updoc', 'DATABASE_ENGINE', fallback='django.db.backends.sqlite3')
DATABASE_NAME = CONFIGURATION.get('updoc', 'DATABASE_NAME', fallback=None)
if not DATABASE_NAME:
    DATABASE_NAME = join(ROOT_PATH, 'database.sqlite3')
DATABASE_USER = CONFIGURATION.get('updoc', 'DATABASE_USER', fallback='')
DATABASE_PASSWORD = CONFIGURATION.get('updoc', 'DATABASE_PASSWORD', fallback='')
DATABASE_HOST = CONFIGURATION.get('updoc', 'DATABASE_HOST', fallback='')
DATABASE_PORT = CONFIGURATION.get('updoc', 'DATABASE_PORT', fallback='')
ADMIN_EMAIL = CONFIGURATION.get('updoc', 'ADMIN_EMAIL', fallback='admin@example.com')
ES_HOSTS = CONFIGURATION.get('updoc', 'ES_HOSTS', fallback='localhost:9200')
ES_INDEX = CONFIGURATION.get('updoc', 'ES_INDEX', fallback='updoc_dev')
ES_TIKA_EXTENSIONS = CONFIGURATION.get('updoc', 'ES_TIKA_EXTENSIONS', fallback='pdf,html,doc,odt,rtf,epub')
ES_MAX_SIZE = CONFIGURATION.getint('updoc', 'ES_MAX_SIZE', fallback=30 * 1024 * 1024)
ES_DOC_TYPE = CONFIGURATION.get('updoc', 'ES_DOC_TYPE', fallback='document')
ES_PLAIN_EXTENSIONS = CONFIGURATION.get('updoc', 'ES_PLAIN_EXTENSIONS', fallback='txt,csv,md,rst')
ES_EXCLUDED_DIR = CONFIGURATION.get('updoc', 'ES_EXCLUDED_DIR', fallback='_sources,_static')


# ok, the configuration files are read and used. Go back the classical Django configuration

ADMINS = ((ADMIN_EMAIL, ADMIN_EMAIL), )

__components = urlparse(HOST)

TEMPLATE_DEBUG = DEBUG

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DATABASE_NAME,  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': DATABASE_PORT,  # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [__components.hostname]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = join(ROOT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = join(ROOT_PATH, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '4f4&@pcm_@017&l27o1#4pch-@g15&d@2rs3jccrxr@zd0h1@7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'updoc.djangoproject.middleware.ProxyRemoteUserMiddleware',
    'updoc.djangoproject.middleware.FakeAuthenticationMiddleware',
    'updoc.djangoproject.middleware.BasicAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'updoc.djangoproject.middleware.IEMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'updoc.djangoproject.middleware.DefaultGroupRemoteUserBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'updoc.djangoproject.context_processors.context_user',
    'updoc.djangoproject.context_processors.most_checked',
)

ROOT_URLCONF = 'updoc.djangoproject.root_urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'updoc.djangoproject.wsgi.application'

TEMPLATE_DIRS = (
    abspath(join(dirname(__file__), 'templates')),
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_admin_bootstrapped.bootstrap3',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    # 'django.contrib.admindocs',
    'updoc',
    'south',
    'bootstrap3',
)
BOOTSTRAP3 = {
    'jquery_url': '/static/js/jquery-1.10.2.min.js',
    'base_url': '/static/bootstrap3/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-4',
}

DEFAULT_GROUP = _('Users')


def strip_split(value):
    return list(filter(lambda x: bool(x), [x.strip() for x in value.split(',')]))

ELASTIC_SEARCH = {
    'host': strip_split(ES_HOSTS),
    'index': ES_INDEX,
    'tika_extensions': set(strip_split(ES_TIKA_EXTENSIONS)),
    'max_size': ES_MAX_SIZE,
    'exclude_dir': set(strip_split(ES_EXCLUDED_DIR)),
    'doc_type': ES_DOC_TYPE,
    'plain_extensions': set(strip_split(ES_PLAIN_EXTENSIONS)),
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}