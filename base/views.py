from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.template import RequestContext
from django.core.urlresolvers import reverse

import django.contrib.messages as messages

from base.forms import ClaimForm, ProfileForm
from base.models import Wiki, Membership
from base.helpers import wiki_id_to_short_id, short_id_to_wiki_id, user_auth_active,\
                         get_gravatar_link
from django.contrib.auth.models import User

#TODO: Whatever we use this for, contain it in the django_rpx_plus app.
from django_rpx_plus.models import RpxData

from recaptcha.client import mailhide

import re #for match

def home(request):
    return render_to_response('base/home.html', {
                              }, 
                              context_instance = RequestContext(request))

def signup(request):
    #If user is logged in and active then show step 2:
    if request.user.is_authenticated() and request.user.is_active:
        if request.method == 'POST':
            form = ClaimForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                #print data
                
                w = Wiki()
                w.tag = data['subdomain']
                w.name = data['title']
                w.save()

                #We also add the user to this wiki as admin.
                m = Membership(user = request.user, wiki = w, permission = 'administrator')
                m.save()

                #TODO: Show success message on wiki
                return HttpResponseRedirect('http://'+w.tag+'.'+request.get_host()+'/')
        else: 
            form = ClaimForm(initial = {'subdomain': 'mywiki',
                                        'title': 'My Excellent Wiki',})

        return render_to_response('base/signup_step2.html', {
                                    'form': form,
                                  }, 
                                  context_instance = RequestContext(request))

    #Otherwise, show a login step.
    extra = {'next': reverse('signup')}
    return render_to_response('base/signup_step1.html', {
                                'extra': extra,
                              }, 
                              context_instance = RequestContext(request))

def user_profile(request, username):
    try:
        u = User.objects.get(username = username)
    except User.DoesNotExist:
        return redirect('home')

    u.avatar = get_gravatar_link(u.email)
    u.mailhide = mailhide.ashtml(u.email, settings.MAILHIDE_PUBLIC_KEY, settings.MAILHIDE_PRIVATE_KEY)

    return render_to_response('base/user_profile.html', {
                                'profile': u,
                              }, 
                              context_instance = RequestContext(request))

def edit_user_profile(request):
    #TODO: Should use auth decorator instead of this:
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponseRedirect(reverse('auth_login'))

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            #print data

            request.user.get_profile().name = data['name']
            request.user.email = data['email']
            try:
                #Check for http:// in the front
                if not re.match(r'^http://', data['website']):
                    data['website'] = 'http://'+data['website']
                request.user.get_profile().website = data['website']
            except KeyError:
                #Do nothing
                pass
            request.user.get_profile().save()
            request.user.save()

            #Set success message.
            messages.success(request, 'Your profile was successfully updated.')

    else: 
        #Try to pre-populate the form with user data.
        form = ProfileForm(initial = {
            'name': request.user.get_profile().name,
            'email': request.user.email,
            'website': request.user.get_profile().website,
        })
    
    request.user.avatar = get_gravatar_link(request.user.email)

    #Also get number of logins associated with account.
    #TODO: Make this a helper in django_rpx_plus.
    request.user.num_logins = RpxData.objects.filter(user = request.user).count()

    return render_to_response('base/change_profile.html', {
                                'form': form,
                              },
                              context_instance = RequestContext(request))

def delete_associated_login(request, rpxdata_id):
    #TODO: Should use auth decorator instead of this:
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponseRedirect(reverse('auth_login'))

    #Check to see if the rpxdata_id exists and is associated with this user
    try:
        #We only allow deletion if user has more than one login
        num_logins = RpxData.objects.filter(user = request.user).count()
        if num_logins > 1:
            r = RpxData.objects.get(id = rpxdata_id, user = request.user)

            #Set success message.
            messages.success(request, 'Your '+r.provider+' login was successfully deleted.')

            #Actually delete
            r.delete()
    except RpxData.DoesNotExist:
        #Silent error, just redirect since message framework can't handle errors
        #yet.
        pass

    return HttpResponseRedirect(reverse('auth_associate'))

def admin_instructions(request):
    return render_to_response('base/admin_instructions.html', {
                              }, 
                              context_instance = RequestContext(request))
