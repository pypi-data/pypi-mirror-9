from django.conf.urls import patterns, url

from mobile_framework.user.views import (
    ListCreateAppUser, RetrieveUpdateAppUser, CreateUserProgression, 
    LoginMobileUser, LogoutUser)

urlpatterns = patterns('',
    url(r'^$', ListCreateUser.as_view()),
    url(r'^progressions/$', CreateUserProgression.as_view()),
    url(r'^login/$', LoginMobileUser.as_view()),
    url(r'^logout/$', LogoutUser.as_view()),
    url(r'^(?P<pk>.+)/$', RetrieveUpdateUser.as_view()),
)
