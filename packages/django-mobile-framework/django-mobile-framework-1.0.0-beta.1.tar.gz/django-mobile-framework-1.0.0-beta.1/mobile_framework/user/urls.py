from django.conf.urls import patterns, url

from mobile_framework.user.views import (
    ListCreateUser, CreateUserProgression, RetrieveUpdateUser, AuthenticateUser
)

urlpatterns = patterns('',
    url(r'^$', ListCreateUser.as_view()),
    url(r'^progressions/$', CreateUserProgression.as_view()),
    url(r'^authenticate/$', AuthenticateUser.as_view()),
    url(r'^(?P<pk>.+)/$', RetrieveUpdateUser.as_view()),
)
