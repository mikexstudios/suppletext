from django import forms
from django.conf import settings

from base.models import Wiki

#import re

class ClaimForm(forms.Form):
    subdomain = forms.RegexField(regex = r'^[a-z0-9]+$', #lowercase + num
                                 max_length = 50, label = 'Subdomain')
    title = forms.CharField(max_length = 255, label = 'Wiki Title')

    def clean_subdomain(self):
        '''
        Check to make sure subdomain hasn't been claimed or the tag has not
        been reserved..
        '''
        subdomain = self.cleaned_data['subdomain']
        try:
            #Check to see if tag is reserved.
            if subdomain not in settings.RESERVED_SITE_TAGS:
                Wiki.objects.get(tag = subdomain)
            
            raise forms.ValidationError(
                    "Sorry, that wiki already exists! Please try another subdomain."
                  )
        except Wiki.DoesNotExist:
            return subdomain

class ProfileForm(forms.Form):
    name = forms.CharField(required = False, max_length = 60, label = 'Name')
    #Hm, max_length of email should be 320... but django's default is 75...
    email = forms.EmailField(max_length = 75, label = 'Email')
    website = forms.URLField(required = False)
    #Password?

