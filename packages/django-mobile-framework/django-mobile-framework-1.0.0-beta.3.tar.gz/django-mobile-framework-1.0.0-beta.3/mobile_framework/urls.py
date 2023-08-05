from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^appusers/', include('mobile_framework.user.appuser_urls')),
    url(r'^users/', include('mobile_framework.user.user_urls')),
    url(r'^devices/', include('mobile_framework.device.urls'))
)
