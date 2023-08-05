from django.conf.urls import patterns, url

from mobile_framework.device.views import CreateDevice, RetrieveUpdateDevice 

urlpatterns = patterns('',
    url(r'^$', CreateDevice.as_view()),
    url(r'^(?P<uuid>.+)/$', RetrieveUpdateDevice.as_view())
)
