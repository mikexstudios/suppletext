from django.conf.urls.defaults import *
from django.conf import settings

import wiki_admin.views

urlpatterns = patterns('wiki_admin.views',
    url(r'^$', 'home', name='wiki-admin-home'), #default url
    url(r'^settings/$', 'settings_', name='wiki-admin-settings'),
    url(r'^users/$', 'users', name='wiki-admin-users'),
    url(r'^users/delete/(?P<username>\w+)/$', 'delete_user', name='wiki-admin-delete-user'),
)
