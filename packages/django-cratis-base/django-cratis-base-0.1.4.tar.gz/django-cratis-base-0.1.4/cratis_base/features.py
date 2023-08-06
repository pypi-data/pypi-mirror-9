from cratis.features import Feature
from django.conf.urls import patterns, url


class Common(Feature):
    """
    This feature is used by most of the django-applications
    """

    def __init__(self, sites_framework=False):
        self.sites_framework = sites_framework


    def configure_settings(self):
        self.append_apps([
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'cratis_base',
            'south',
        ])

        self.settings.MIDDLEWARE_CLASSES = (
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        )

        s = self.settings

        s.STATIC_URL = '/static/'
        s.STATIC_ROOT = s.BASE_DIR + '/var/static'

        s.MEDIA_URL = '/media/'
        s.MEDIA_ROOT = s.BASE_DIR + '/var/media'



        if self.sites_framework:
            self.append_apps([
                'django.contrib.sites',
            ])
            s.SITE_ID = 1

    def configure_urls(self, urls):
        if self.settings.DEBUG:
            urls += patterns('',
                url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': self.settings.MEDIA_ROOT}),
                url(r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': self.settings.STATIC_ROOT}),
            )

class AdminArea(Feature):

    def __init__(self, prefix='admin'):
        super(AdminArea, self).__init__()
        self.prefix = r'^%s/' % prefix

    def configure_settings(self):
        self.append_apps(['django.contrib.admin'])

    def configure_urls(self, urls):

        from django.conf.urls import patterns, url, include
        from django.contrib import admin

        admin.autodiscover()

        urls += patterns('',
            url(self.prefix, include(admin.site.urls)),
        )
