from django.conf.urls import patterns, url

from mobile_framework.user.views import (
    ListCreateUser, RetrieveUpdateUser, LoginUser, LogoutUser)

urlpatterns = patterns('',
    url(r'^$', ListCreateUser.as_view()),
    url(r'^login/$', LoginUser.as_view()),
    url(r'^logout/$', LogoutUser.as_view()),
    url(r'^(?P<pk>.+)/$', RetrieveUpdateUser.as_view()),
)
