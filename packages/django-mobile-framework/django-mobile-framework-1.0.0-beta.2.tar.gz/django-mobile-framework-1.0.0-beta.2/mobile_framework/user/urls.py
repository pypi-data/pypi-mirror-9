from django.conf.urls import patterns, url

from mobile_framework.user.views import (
    ListCreateUser, CreateUserProgression, RetrieveUpdateUser, LoginUser,
    LoginMobileUser, LogoutUser)

urlpatterns = patterns('',
    url(r'^$', ListCreateUser.as_view()),
    url(r'^progressions/$', CreateUserProgression.as_view()),
    url(r'^login/$', LoginUser.as_view()),
    url(r'^login/mobile/$', LoginMobileUser.as_view()),
    url(r'^logout/$', LogoutUser.as_view()),
    url(r'^(?P<pk>.+)/$', RetrieveUpdateUser.as_view()),
)
