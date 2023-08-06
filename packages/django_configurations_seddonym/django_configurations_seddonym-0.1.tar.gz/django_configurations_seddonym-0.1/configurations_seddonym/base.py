"""Base settings shared by all environments.
This is a reusable basic settings file.
"""
from configurations import Configuration
from . import mixins


class StandardConfiguration(mixins.UnifiedDebugMixin,
                        mixins.SecretSettingsMixin,
                        mixins.AllowedHostsMixin,
                        mixins.LoggingMixin,
                        mixins.DatabaseMixin,
                        mixins.StaticMediaAndTemplatesMixin,
                        mixins.EmailMixin,
                        mixins.BaseUrlMixin,
                        Configuration):
    """A configuration that collects together lots of standard
    configuration patterns for use across projects."""

    TIME_ZONE = 'GB'
    USE_TZ = True
    USE_I18N = True
    USE_L10N = True
    LANGUAGE_CODE = 'en-GB'
    LANGUAGES = (
        ('en-GB', 'British English'),
    )

    SITE_ID = 1
    LOGIN_URL = '/login/'
    LOGOUT_URL = '/logout/'
    LOGIN_REDIRECT_URL = '/'

    STATIC_URL = '/static/'
    MEDIA_URL = '/uploads/'

    TEMPLATE_CONTEXT_PROCESSORS = Configuration.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
    )

    ROOT_URLCONF = 'urls'

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
    )

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

    PROTOCOL = 'http'

    MANAGERS = ADMINS = (
        ('David Seddon', 'david@seddonym.me'),
    )
