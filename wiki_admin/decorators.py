try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.3, 2.4 fallback.

#from django.contrib.auth import REDIRECT_FIELD_NAME
#from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
#from django.utils.http import urlquote
import django.contrib.messages as messages

#The reason why we use django's urlencode instead of urllib's urlencode is that
#django's version can operate on unicode strings.
from django.utils.http import urlencode

#from django.shortcuts import render_to_response
#from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.conf import settings

def admin_permission_required(perm):
    """
    Decorator for wiki admin views that execute common tasks. Also checks for
    admin permission.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            #Check if user has permission to access the admin
            request.user.required_role = None #clear out any existing setting
            if request.user.has_perm('wiki_admin.%s' % perm, settings.WIKI):
                return view_func(request, *args, **kwargs)

            #Otherwise, user does not have permission 
            #Is user logged in?
            if not request.user.is_authenticated():
                messages.info(request, 'If you are an administrator of this wiki, please login.')
            else:
                #User is logged in but doesn't have admin priviledges to this wiki.
                messages.error(request, 'Your do not have administrator privileges to this wiki.')
            destination = urlencode({'next': 'http://'+request.get_host()+request.get_full_path() })
            return HttpResponseRedirect(reverse('auth_login')+'?'+destination)
        return wraps(view_func)(_wrapped_view)
    return decorator
