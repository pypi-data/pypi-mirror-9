from django.conf.urls import patterns, url, include

from django.contrib import admin


urlpatterns = patterns(
    '',
    url('^admin/', include(admin.site.urls)),
)
