from django.conf.urls import patterns, url
from .views import cloak, uncloak, login

urlpatterns = patterns('',
    url(r'^cloak$', cloak, name="cloak"),
    url(r'^cloak/(?P<pk>.+)$', cloak, name="cloak"),
    url(r'^uncloak$', uncloak, name="uncloak"),
    url(r'^login/(?P<signature>.*)$', login),
)
