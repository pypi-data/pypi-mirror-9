from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(pattern_name='cas_login', permanent=False)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('mama_cas.urls')),
)
