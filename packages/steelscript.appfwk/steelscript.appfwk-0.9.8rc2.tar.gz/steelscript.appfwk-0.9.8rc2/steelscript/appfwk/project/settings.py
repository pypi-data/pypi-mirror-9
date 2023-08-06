# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


# Django settings for SteelScript project project.
import os
import sys
import pkg_resources

# version information
VERSION = pkg_resources.get_distribution("steelscript.appfwk").version

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SETTINGS_ROOT = os.path.abspath(__file__)
PORTAL_ROOT = os.path.dirname(SETTINGS_ROOT)
PROJECT_ROOT = os.path.dirname(PORTAL_ROOT)

# Development defaults
DATAHOME = os.getenv('DATAHOME', PROJECT_ROOT)
DATA_CACHE = os.path.join(DATAHOME, 'data', 'datacache')
INITIAL_DATA = os.path.join(DATAHOME, 'data', 'initial_data')
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

AUTH_USER_MODEL = 'preferences.PortalUser'
LOGIN_REDIRECT_URL = '/report'

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',

        # Path to database file if using sqlite3.
        # Database name for others
        'NAME': os.path.join(PROJECT_ROOT, 'project.db'),

        'USER': '',      # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'datacache')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# If you set this to True, templates will look for local copies of the JS libs
# that we normally get off the cloud.
OFFLINE_JS = False

JS_VERSIONS = {
    'jquery': '1.9.1',
    'jqueryui': '1.10.2',
    'jqueryform': '3.32',
    'yui': '3.17.2',
}

# Format: (url, dirname). If dirname is None, "steel appfwk mkproject" will
# install the file directly into the offline JS dir. Otherwise, it will treat
# the file as a zip or tar archive and extract it into that subdirectory.
OFFLINE_JS_FILES = [
    ("http://ajax.googleapis.com/ajax/libs/jquery/{0}/jquery.min.js".format(JS_VERSIONS['jquery']), None),
    ("http://ajax.googleapis.com/ajax/libs/jquery/{0}/jquery.min.map".format(JS_VERSIONS['jquery']), None),
    ("http://jqueryui.com/resources/download/jquery-ui-{0}.zip".format(JS_VERSIONS['jqueryui']), "jquery-ui"),
    ("http://cdnjs.cloudflare.com/ajax/libs/jquery.form/{0}/jquery.form.js".format(JS_VERSIONS['jqueryform']), None),
    ("http://yui.zenfs.com/releases/yui3/yui_{0}.zip".format(JS_VERSIONS['yui']), "yui"),
]


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'media'),
    os.path.join(PROJECT_ROOT, 'thirdparty'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'yc6!d7figlp%$$mhjio-9hn$zr9ot+zp)y8)un)rt^rukcwm^t'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'steelscript.appfwk.apps.report.middleware.exceptions.ReloadExceptionHandler',
    'steelscript.appfwk.apps.report.middleware.timezones.TimezoneMiddleware',
    #'project.middleware.LoginRequiredMiddleware',
)

ROOT_URLCONF = 'steelscript.appfwk.project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'steelscript.appfwk.project.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'steelscript.appfwk.project.context_processors.offline_js',
    'steelscript.appfwk.project.context_processors.versions',
    'steelscript.appfwk.apps.report.context_processors.report_list_processor',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # third-party apps
    'rest_framework',
    'django_extensions',
    'django_ace',
    'announcements',

    # portal apps
    'steelscript.appfwk.apps.datasource',
    'steelscript.appfwk.apps.devices',
    'steelscript.appfwk.apps.report',
    'steelscript.appfwk.apps.geolocation',
    'steelscript.appfwk.apps.help',
    'steelscript.appfwk.apps.preferences',
    'steelscript.appfwk.apps.plugins',
    'steelscript.appfwk.apps.alerting',

    # 'standard' plugins
    'steelscript.appfwk.apps.plugins.builtin.whois',
    'steelscript.appfwk.apps.plugins.builtin.solarwinds',
    'steelscript.appfwk.apps.plugins.builtin.sharepoint',
)

ADMIN_TOOLS_MENU = 'steelscript.appfwk.project.menu.CustomMenu'
ADMIN_TOOLS_THEMING_CSS = 'css/theming.css'
ADMIN_TOOLS_INDEX_DASHBOARD = 'steelscript.appfwk.project.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'steelscript.appfwk.project.dashboard.CustomAppIndexDashboard'

from steelscript.appfwk.apps.plugins.loader import load_plugins
load_plugins()

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],

    'EXCEPTION_HANDLER':
        'steelscript.appfwk.project.middleware.authentication_exception_handler'
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
from logging.handlers import SysLogHandler

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)-5s] %(thread)d %(name)s:%(lineno)s - %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'standard_syslog': {
            #'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            'format': '%(asctime)s SteelScript AppFramework: [%(levelname)-5s] %(name)s:%(lineno)s - %(message)s',
            'datefmt': '%b %d %H:%M:%S',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'steelscript.appfwk.project.nullhandler.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,            # 5 MB
            'backupCount': 1,
            'formatter': 'verbose',
            'filename': os.path.join(PROJECT_ROOT, 'log.txt')
        },
        'backend-log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,            # 5 MB
            'backupCount': 1,
            'formatter': 'standard',
            'filename': os.path.join(PROJECT_ROOT, 'log-db.txt')
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['backend-log'],
            'level': 'DEBUG',
            'propagate': False,
        },
        '': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

GLOBAL_ERROR_HANDLERS = (
    {'sender': 'LoggingSender',
     'template': 'Error processing job: {message}'},
)

#
# App Framework custom settings
#

# Strip device passwords from fixture that gets written to disk.  Should remain
# True in all production settings.  If False, the passwords will be stored to
# disk to aid in development workflows.
APPFWK_STRIP_DEVICE_PASSWORDS = True

# Job aging parameters
# Used as a form of datasource caching, jobs older than the 'ancient'
# threshold will be deleted regardless, while 'old' jobs will
# only be deleted if no other jobs are referencing their data.
APPS_DATASOURCE = {
    'job_age_old_seconds': 60*60*24,            # one day
    'job_age_ancient_seconds': 7*60*60*24,      # one week
    'threading': True
}

TESTING = 'test' in sys.argv

LOCAL_APPS = None
