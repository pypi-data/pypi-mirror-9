import os


class LocalMixin(object):
    """Mixin designed for local installation, that uses the Django dev server.
    """
    DEBUG = True
    DOMAIN = 'localhost'
    PORT = '8000'
    MANAGERS = ADMINS = (
        ('David Seddon', 'david@seddonym.me'),
    )

    STATIC_ROOT = ''

    @property
    def STATICFILES_DIRS(self):
        return (os.path.join(self.PROJECT_ROOT, 'static'),)

    @property
    def COMPRESS_ROOT(self):
        return os.path.join(self.PROJECT_ROOT, 'compressed')

    @property
    def LOG_PATH(self):
        return os.path.join('/var/log/django', self.PROJECT_NAME)




class WebfactionMixin(object):
    """Mixin designed for sites hosted on Webfaction using the 
    nginx / uwsgi approach.
    
    Required:
    
        WEBFACTION_USER
        WEBFACTION_APPNAME
    """

    @property
    def PROJECT_ROOT(self):
        return '/home/%s/webapps/%s/project' % (self.WEBFACTION_USER,
                                                self.WEBFACTION_APPNAME)

    @property
    def STATICFILES_DIRS(self):
        return (os.path.join(self.PROJECT_ROOT, 'static'),)

    @property
    def LOG_PATH(self):
        return '/home/%s/logs/user/%s/' % (self.WEBFACTION_USER,
                                           self.WEBFACTION_APPNAME)

    @property
    def STATIC_ROOT(self):
        return '/home/%s/webapps/%s/static' % (self.WEBFACTION_USER,
                                               self.WEBFACTION_APPNAME)

    @property
    def MEDIA_ROOT(self):
        return '/home/%s/webapps/%s/uploads' % (self.WEBFACTION_USER,
                                                self.WEBFACTION_APPNAME)

    @property
    def DEFAULT_DATABASE_NAME(self):
        return '%s_%s' % (self.PROJECT_NAME, self.WEBFACTION_APPNAME)

    @property
    def DEFAULT_DATABASE_USER(self):
        return self.DEFAULT_DATABASE_NAME


class WebfactionDevMixin(WebfactionMixin):
    """Mixin designed for dev site hosted on Webfaction using the 
    nginx / uwsgi approach.
    
    Required:
    
        WEBFACTION_USER
    """
    DEBUG = True
    WEBFACTION_APPNAME = 'dev'


class WebfactionLiveMixin(WebfactionMixin):
    """Mixin designed for live site hosted on Webfaction using the 
    nginx / uwsgi approach.
    
    Required:
    
        WEBFACTION_USER
    """
    DEBUG = False
    WEBFACTION_APPNAME = 'live'
