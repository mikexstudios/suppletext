from django import forms
from django.conf import settings

from django.contrib.auth.models import User
#from base.models import Wiki

#import re

class SettingsForm(forms.Form):
    name = forms.CharField(required = False, max_length = 60, label = 'Wiki Name')
    tagline = forms.CharField(required = False, max_length = 140, label = 'Tagline')
    front_page = forms.CharField(max_length = 100, label = 'Front Page')
    
    default_view = forms.ChoiceField(choices = settings.PERMISSION_CHOICES, 
                                     label = 'Default view role')
    default_edit = forms.ChoiceField(choices = settings.PERMISSION_CHOICES, 
                                      label = 'Default edit role')
    default_special = forms.ChoiceField(choices = settings.PERMISSION_CHOICES, 
                                      label = 'Default special role')

class UsersForm(forms.Form):
    username = forms.CharField(max_length = 30, label = 'Contributor Username')
    user_role = forms.ChoiceField(choices = settings.USER_ROLE_CHOICES, 
                                  label = 'User role')
    def clean_username(self):
        '''
        Check to make sure username exists.
        '''
        username = self.cleaned_data['username']
        try:
            u = User.objects.get(username = username)
        except User.DoesNotExist:
            raise forms.ValidationError("The user you are adding does not exist!")
        
        #Would also like to check to see if user has already been added, but can't
        #check that here since don't have access to request object.

        return username
