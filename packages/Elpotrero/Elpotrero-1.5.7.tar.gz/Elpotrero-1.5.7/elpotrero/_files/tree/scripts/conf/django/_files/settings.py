"""
Django settings for {{project}} project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
import sys

from settings_local import *
from settings_media import *

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.webdesign',
    'django_countries',

    'debug_toolbar',
    'south',
    'mediagenerator',
    'gunicorn',

    # this is app needs to be installed by me
    'utils',
)


# After the MIDDLEWARE_CLASSES and TEMPLATE_DIRS variables are declared
# I extend them with variables I created in settings_local
#
# This is not very elegant, but the reason I do it this way, is because
# if I just try to add on to MIDDLEWARE_CLASSES, or TEMPALTE_DIRS, then
# this file doesn't know about it yet see settings_local gets called before
# settings.py has finished loading, so that variable hasn't been initialized
# properly yet  instead I created this variable, which does get fully loaded,
# so I can call it from settings.py

MIDDLEWARE_CLASSES = [
    # Media middleware has to come first
    'mediagenerator.middleware.MediaMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

MIDDLEWARE_CLASSES.extend(MIDDLEWARE_CLASSES_ADDON)

TEMPLATE_DIRS = [
    # Put strings here, like "/home/html/django_templates"
    #    or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'templates'),
]

TEMPLATE_DIRS.extend(TEMPLATE_DIRS_ADDON)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

# there is no need to put this in settings_local, since "project" is used
# across different branches.
ROOT_URLCONF = '{{project}}.urls'
WSGI_APPLICATION = '{{project}}.wsgi.application'

# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
# this is located in settings_local

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
# this is located in settings_local
# django-shop variables
