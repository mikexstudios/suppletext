from django.conf.urls.defaults import *
from django.conf import settings

import base.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    url(r'^$', base.views.home, name='home'), #default url
    url(r'^signup/$', base.views.signup, name='signup'),
    
    #When we include other urls.py, we must use name captured parameters.
    #url(r'^admin/$', base.views.admin_instructions, name='admin-instructions'),
    #(r'^admin/', include('wiki_admin.urls')),

    url(r'^user/(\w+)/$', base.views.user_profile, name='user-profile'),

    url(r'^accounts/$', 'django.views.generic.simple.redirect_to', 
                        {'url': '/accounts/profile/', 'permanent': False},
                        name='auth_home'),
    url(r'^accounts/profile/$', base.views.edit_user_profile, name='edit-user-profile'),
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

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
