try:
    from functools import update_wrapper, wraps
except ImportError:
    from django.utils.functional import update_wrapper, wraps  # Python 2.3, 2.4 fallback.

#from django.contrib.auth import REDIRECT_FIELD_NAME
#from django.http import HttpResponseRedirect
#from django.utils.http import urlquote

from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings
#from django.contrib.auth.models import User
from .models import Page

def wiki_permission_required(perm):
    '''
    Decorator for wiki views that checks whether a user has a particular
    permission enabled, redirecting to the log-in page if necessary.
    '''
    def decorator(view_func):
        def _wrapped_view(request, page_tag, *args, **kwargs):
            #Check if the user has the required permission given the
            #page object.
            #TODO: Figure out a way to eliminate the redundancy of querying
            #      for the page object twice.
            try:
                p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
            except IndexError:
                #If page doesn't exist, we pass a dummy Page object in so that we
                #use global perm. We need to set the Wiki object.
                p = Page(wiki = settings.WIKI)
            
            request.user.required_role = None #clear out any existing setting
            if request.user.has_perm('page.can_%s' % perm, p):
                return view_func(request, page_tag, *args, **kwargs)
            #Otherwise, user does not have permission. We want to display a
            #helpful message to the user, so we want to get what role is
            #required in order to perform the action. Luckily, our has_perm
            #backend slips in the perm required in user obj.
            try:
                required_role = request.user.required_role
            except AttributeError:
                #We shouldn't get here.
                raise Exception('WikiPermBackend not behaving correctly!')

            #We need the full url here. Our rpx response goes back to the
            #root domain so we want to redirect back here.
            extra = {'next': 'http://'+request.get_host()+request.get_full_path() }
            
            return render_to_response('wiki/perm_required.html', {
                                        'required_role': required_role,
                                        'intended_action': perm,
                                        'extra': extra,
                                      }, 
                                      context_instance = RequestContext(request))
        return wraps(view_func)(_wrapped_view)
    return decorator
  
