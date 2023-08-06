import os
from .utils import settings_from_module


class UnifiedDebugMixin(object):
    """Configuration mixin for making the thumbnail and template debug
    equal to the normal debug setting.
    """
    @classmethod
    def setup(cls):
        super(UnifiedDebugMixin, cls).setup()
        # Unify all debug settings
        cls.THUMBNAIL_DEBUG = cls.TEMPLATE_DEBUG = cls.DEBUG


class SecretSettingsMixin(object):
    """Configuration mixin for importing the settings from secret.py"""

    @classmethod
    def pre_setup(cls):
        super(SecretSettingsMixin, cls).pre_setup()

        # Set any settings from secret.py
        for name, value in settings_from_module('settings.secret').items():
            setattr(cls, name, value)


class AllowedHostsMixin(object):
    """Configuration mixin for setting ALLOWED_HOSTS.
    
    Usage:
    
        DOMAIN: required.
    """

    @property
    def ALLOWED_HOSTS(self):
        return [self.DOMAIN, 'django-dbbackup']


class LoggingMixin(object):
    """Configuration mixin for setting the logging.
    
    Usage:
    
        LOG_PATH: required.
    """

    @property
    def LOGGING(self):
        error_request_handlers = ['error']
        if not self.DEBUG:
            # Only mail admins if debug is False
            error_request_handlers.append('mail_admins')

        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                    'datefmt' : "%d/%b/%Y %H:%M:%S"
                },
            },
            'handlers': {
                'error': {
                    'level':'ERROR',
                    'class':'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(self.LOG_PATH, 'error.log'),
                    'maxBytes': 50000,
                    'backupCount': 2,
                    'formatter': 'standard',
                },
                'debug': {
                    'level':'DEBUG',
                    'class':'logging.handlers.RotatingFileHandler',
                    'filename': os.path.join(self.LOG_PATH, 'debug.log'),
                    'maxBytes': 50000,
                    'backupCount': 2,
                    'formatter': 'standard',
                },
                'mail_admins': {
                    'level': 'ERROR',
                    'class': 'django.utils.log.AdminEmailHandler',
                    'include_html': True,
                },
            },
            'loggers': {
                'django': {
                    'handlers':['error'],
                    'propagate': True,
                    'level':'DEBUG',
                },
                'django.request': {
                    'handlers': error_request_handlers,
                    'level': 'ERROR',
                    'propagate': False,
                },
                'project': {
                    'handlers':['debug'],
                    'propagate': True,
                    'level':'DEBUG',
                },
            }
        }


class DatabaseMixin(object):
    """Configuration mixin for setting the databases.
    
    Usage:
    
        PROJECT_NAME: setting for the user and database name
        DEFAULT_DATABASE_PASSWORD: setting for the database password; should
                                   be defined in secret.py.
    """
    @property
    def DATABASES(self):
        return {
            'default': {
                'NAME': self.DEFAULT_DATABASE_NAME,
                'USER': self.DEFAULT_DATABASE_USER,
                'PASSWORD': self.DEFAULT_DATABASE_PASSWORD,
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
            }
        }

    @property
    def DEFAULT_DATABASE_NAME(self):
        return self.PROJECT_NAME

    @property
    def DEFAULT_DATABASE_USER(self):
        return self.PROJECT_NAME


class StaticMediaAndTemplatesMixin(object):
    """Configuration mixin for setting the path to the static, media
    and template directories.
    
    Usage:
    
        PROJECT_ROOT: Required.
    """


    @property
    def STATIC_ROOT(self):
        return os.path.join(self.PROJECT_ROOT, 'static')

    @property
    def MEDIA_ROOT(self):
        return os.path.join(self.PROJECT_ROOT, 'uploads')

    @property
    def TEMPLATE_DIRS(self):
        TEMPLATE_DIR = os.path.join(self.PROJECT_ROOT, 'templates')
        return (TEMPLATE_DIR,)


class EmailMixin(object):
    """Configuration mixin for setting the email.
    
    Usage:
    
        SITE_TITLE: Required
        DOMAIN: Required
    """

    @property
    def SERVER_EMAIL(self):
        return 'contact@%s' % self.DOMAIN

    @property
    def DEFAULT_FROM_EMAIL(self):
        return '%s <%s>' % (self.SITE_TITLE, self.SERVER_EMAIL)

    @property
    def CONTACT_EMAIL(self):
        return self.SERVER_EMAIL


class BaseUrlMixin(object):
    """Adds a BASE_URL setting.
    Usage:
    
        DOMAIN: Required
        PORT: Required if running development server
    """

    PROTOCOL = 'http'

    @property
    def BASE_URL(self):
        if getattr(self, 'PORT', ''):
            # Necessary for the development server
            url = "%s:%s" % (self.DOMAIN, self.PORT)
        else:
            url = self.DOMAIN
        return '%s://%s' % (self.PROTOCOL, url)
