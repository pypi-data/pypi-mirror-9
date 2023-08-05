from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^users/', include('mobile_framework.user.urls')),
    url(r'^devices/', include('mobile_framework.device.urls'))
)
