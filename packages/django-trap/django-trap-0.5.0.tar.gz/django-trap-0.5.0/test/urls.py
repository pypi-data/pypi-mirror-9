try:
    from django.conf.urls import patterns, include, url
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include('django_trap.urls', namespace='django_trap')),
    url(r'^secret/', include(admin.site.urls)),
)
