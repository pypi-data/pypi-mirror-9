# local settings for {{project}} project.

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# this is used in the main settings file as well as here
# (GLOBAL_MEDIA_DIRS uses this)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# used for debug_toolbar
INTERNAL_IPS = ('{{address}}',)

PROJECT_STATE = '{{branch}}'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# DEBUG_TOOLBAR_PATCH_SETTINGS = False

ADMINS = (
    ('{{admin_name}}', '{{admin_email}}'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.{{db_engine}}',
        'NAME': '{{project}}_{{branch}}_db',
        'USER': '{{user}}',          # Not used with sqlite3.
        'PASSWORD': '{{db_password}}',     # Not used with sqlite3.
        'HOST': '',
        'PORT': '',
    }
}

SITE_ID = 1

# change this to the sitename when you are using forward
# Only MEDIA_URL and STATIC_URL are using the sitename variable for when
# I have to switch to the forward in development
#
# MEDIA_ROOT and STATIC_ROOT do not need it under any circumstances
#
SITENAME = "{{project}}.{{domain}}"
# SITENAME = "shopdev-ronny.fwd.wf"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '{{rootpath}}/{{project}}.{{domain}}/public/media/dynamic/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://{0}/media/'.format(SITENAME)

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '{{rootpath}}/{{project}}.{{domain}}/public/media/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/" or STATIC_URL = '/static/'
STATIC_URL = 'http://{0}/static/'.format(SITENAME)

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


# this is not very elegant, but the reason I do it this way, is because
# if I just try to add on to MIDDLEWARE_CLASSES, this file doesn't know
# about it yet see settings_local gets called before settings.py has
# finished loading, so that variable hasn't been initialized properly yet
# instead I created this variable, which does get fully loaded,
# so I can call it from settings.py

MIDDLEWARE_CLASSES_ADDON = [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

# Make this unique, and don't share it with anybody.
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '{{secretkey}}'

ALLOWED_HOSTS = []

TEMPLATE_DIRS_ADDON = [
    # Put strings here, like "/home/html/django_templates"
    #    or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "{{rootpath}}/{{project}}.{{domain}}/private/templates"
]

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
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'stream_to_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '{{rootpath}}/{{project}}.{{domain}}/logs/'
                        '{{project}}.django.debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'stream_to_console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'custom.debug': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
