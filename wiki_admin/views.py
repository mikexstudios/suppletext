from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList #for triggering form validation error
import django.contrib.messages as messages

from wiki_admin.forms import SettingsForm, UsersForm
from .decorators import admin_permission_required
#from wiki_admin.models import 
#from wiki_admin.helpers import 
from base.models import Wiki, Membership
from django.contrib.auth.models import User

def home(request):
    #Redirect to whatever should be shown by default.
    return redirect('wiki-admin-settings')

@admin_permission_required('can_admin')
def settings_(request): #postfix _ to not clash with django settings var
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            #print data

            settings.WIKI.name = data['name']
            settings.WIKI.tagline = data['tagline']
            settings.WIKI.front_page = data['front_page']
            settings.WIKI.default_view = data['default_view']
            settings.WIKI.default_edit = data['default_edit']
            settings.WIKI.default_special = data['default_special']
            settings.WIKI.save()

            #Set success message.
            messages.success(request, 'Settings was successfully updated.')

    else: 
        #Try to pre-populate the form with user data.
        #form = GeneralSettingsForm()
        form = SettingsForm(initial = {
            'name': settings.WIKI.name,
            'tagline': settings.WIKI.tagline,
            'front_page': settings.WIKI.front_page,
            'default_view': settings.WIKI.default_view,
            'default_edit': settings.WIKI.default_edit,
            'default_special': settings.WIKI.default_special,
        })

    return render_to_response('wiki_admin/settings.html', {
                                'form': form,
                              }, 
                              context_instance = RequestContext(request))

@admin_permission_required('can_admin')
def users(request):
    if request.method == 'POST':
        form = UsersForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            #print data
            
            #User exists, as checked in the form. We also need to get the user
            #object.
            u = User.objects.get(username = data['username'])

            #We additionally check that the user hasn't already been added.
            #This also takes care of trying to add ourselves.
            try:
                Membership.objects.get(wiki = settings.WIKI, user = u)
                form._errors['username'] = ErrorList(['User has already been added.'])
            except Membership.DoesNotExist:
                #Okay, user has not been added, that's good. Let's add the 
                #membership.
                m = Membership(wiki = settings.WIKI, user = u)
                #We are assuming that all users are admin level so that we don't
                #have to check if they are allowed to add this permission.
                m.permission = data['user_role']
                m.save()

                #Set success message.
                messages.success(request, 'Users was successfully added.')
    else: 
        #Try to pre-populate the form with user data. Use initial = {}
        form = UsersForm()

    #Get list of users added to this wiki.
    members = Membership.objects.filter(wiki = settings.WIKI)

    return render_to_response('wiki_admin/users.html', {
                                'form': form,
                                'members': members,
                              }, 
                              context_instance = RequestContext(request))

#TODO: Delete user, but think about CSRF protection.
@admin_permission_required('can_admin')
def delete_user(request, username):
    #Make sure user exists and has membership.
    try:
        #Check that we aren't deleting ourselves.
        if username != request.user.username:
            u = User.objects.get(username = username)
            m = Membership.objects.get(wiki = settings.WIKI, user = u)
            m.delete()
            messages.success(request, 'User successfully deleted from wiki.')
        else:
            messages.error(request, "Nice try, but you shouldn't delete yourself!")
    except User.DoesNotExist:
        messages.error(request, 'The user you are trying to delete does not exist.')
    except Membership.DoesNotExist:
        messages.error(request, 'The user you are trying to delete is not a member of this wiki.')

    return redirect('wiki-admin-users')



