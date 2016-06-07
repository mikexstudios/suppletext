from django import forms
from django.conf import settings

from wiki.models import Page

#import re

class EditForm(forms.Form):
    content = forms.CharField(required = False, widget = forms.Textarea, label = 'Page Content')
    note = forms.CharField(required = False, max_length = 140, label = 'Page Note')
    #Keeps track of when the page was edited so that we can resolve conflicts.
    time = forms.DateTimeField(widget = forms.HiddenInput)
    #We use latest time to keep track of the time of the latest edit. This will
    #allow us to determine if a page has been edited after the user views the
    #conflict.
    latest_time = forms.DateTimeField(required = False, widget = forms.HiddenInput)
    
class PagePermissionsForm(forms.Form):
    #There is a problem where a a user of lower level sets permission to a higher
    #level. Then user gets locked out...
    _permission_choices = list(settings.PERMISSION_CHOICES)
    _permission_choices.insert(0, ('default', 'Global setting (default)'))

    view = forms.ChoiceField(required = False, choices = _permission_choices, 
                                     label = 'View role')
    edit = forms.ChoiceField(required = False, choices = _permission_choices,
                                      label = 'Edit role')
    #Since special features are important, maybe we always limit them to
    #contributors or higher
    #special = forms.ChoiceField(required = False, choices = _permission_choices,
    #                                  label = 'Special role')
