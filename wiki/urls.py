from django.conf.urls.defaults import *
from django.conf import settings

import wiki.views

urlpatterns = patterns('wiki.views',
    url(r'^$', 'home', name='home'), #default url
    url(r'^(\S+):show/$', 'show'), #don't specify name
    url(r'^(\S+):show/([a-z0-9]+)/$', 'show', name='show'), 
    url(r'^(\S+):revert/([a-z0-9]+)/$', 'revert', name='revert'), 
    url(r'^(\S+):edit/$', 'edit', name='edit'), 
    url(r'^(\S+):edit/([a-z0-9]+)/$', 'edit', name='edit'), 
    url(r'^(\S+):history/$', 'history', name='history'), 
    url(r'^(\S+):compare/$', 'compare', name='compare'), 
    url(r'^(\S+):compare/([a-z0-9]+)/([a-z0-9]+)/$', 'compare', name='compare'), 
    url(r'^(\S+):permissions/$', 'change_page_permissions', name='page-permissions'), 
)

urlpatterns += patterns('',
    #url(r'^admin/$', 'base.views.admin_instructions', name='admin-instructions'),
    (r'^admin/', include('wiki_admin.urls')),

    url(r'^user/(\w+)/$', 'base.views.user_profile', name='user-profile'),
    url(r'^accounts/$', 'django.views.generic.simple.redirect_to', 
                        {'url': '/accounts/profile/', 'permanent': False},
                        name='auth_home'),
    url(r'^accounts/profile/$', 'base.views.edit_user_profile', name='edit-user-profile'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', 
                      {'template_name': 'django_rpx_plus/logged_out.html'}, 
                      name='auth_logout'),
    #url(r'^accounts/associate/delete/(\d+)/$', base.views.delete_associated_login, name='delete-associated-login'),
    (r'^accounts/', include('django_rpx_plus.urls')),

    #Temporary fix for serving static files in dev environment.
    #See: http://docs.djangoproject.com/en/dev/howto/static-files/
    #In production setting, the webserver automatically overrides this, 
    #so there is no need to take this out when in production:
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('wiki.views',
    #A catch-all to handle pages.
    #TODO: Incorporate multi-level catching.
    url(r'^(\S+)/$', 'show', name='show'),
)
