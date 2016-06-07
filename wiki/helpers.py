from django.conf import settings 
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from datetime import datetime

from wiki.models import Page
from base.helpers import BaseConverter
from base.models import Membership
import wiki.utils.diff as diff

import re

def context_processor(request):
    '''
    Not called directly, but used by django's context_processor.
    Remember: Add this function in settings.
    '''
    template_vars =  {
        'media_path': settings.MEDIA_URL.rstrip('/'),
        'base_media_path': settings.BASE_MEDIA_URL.rstrip('/'),
        'wiki_media_path': settings.WIKI_MEDIA_URL.rstrip('/'),
        'wiki_admin_media_path': settings.WIKI_ADMIN_MEDIA_URL.rstrip('/'),
        'wiki': settings.WIKI,
        'admin_perms': WikiAdminPermWrapper(request.user, settings.WIKI),
    }

    return template_vars

#NOTE: Currently, not used.
class WikiPermWrapper(object):
    def __init__(self, user, page_tag):
        self.user = user
        self.page_tag = page_tag
        #Get page object
        try:
            self.page = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
        except IndexError:
            #If page doesn't exist, we pass a dummy Page object in so that we
            #use global perm. We need to set the Wiki object.
            self.page = Page(wiki = settings.WIKI)
 
    def __getitem__(self, perm):
        return self.user.has_perm(perm, self.page)
        
    def __iter__(self):
        raise TypeError("WikiPermWrapper is not iterable.")

#TODO: Move this into wiki_admin/context_processors.py?
class WikiAdminPermWrapper(object):
    def __init__(self, user, wiki):
        self.user = user
        self.wiki = wiki
 
    def __getitem__(self, perm):
        return self.user.has_perm(perm, self.wiki)
        
    def __iter__(self):
        raise TypeError("WikiAdminPermWrapper is not iterable.")

def unified_diff(str1, str2):
    '''
    Given two strings (they can include linebreaks), return a list of tuples
    of the form:
    [({'base': {'start': int, 'total_lines': int},
       'changed': {'start': int, 'total_lines': int}},
      diff object),
     ...]
     See compare.html template for how this data structure can be used.
    '''
    #Compute diff using unified diff format. Need to have the content be list
    #of strings.
    str1_list = str1.splitlines() #True = keepends
    str2_list = str2.splitlines()
    diffs = diff.diff_blocks(str1_list, str2_list, settings.DIFF_CONTEXT_LINES)

    #Generate @@ a,b a,b @@ string
    #a = start line of chunk ; b = total lines in chunk
    for i, d in enumerate(diffs):
        base_range = {}
        changed_range = {}

        base_range['start'] = d[0]['base']['offset'] + 1
        changed_range['start'] = d[0]['changed']['offset'] + 1

        base_range['total_lines'] = 0
        changed_range['total_lines'] = 0
        for change in d:
            base_range['total_lines'] += len(change['base']['lines'])
            changed_range['total_lines'] += len(change['changed']['lines'])
        
        #Since we can't dynamically get indices in template, we have to "zip"
        #this data with diffs and grab it at the same time in compare.html
        diffs[i] = ({'base': base_range, 'changed': changed_range},
                    d)

    return diffs

def pretty_date(time = False, within_week = False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc

    Written by: http://evaisse.com/post/93417709/python-pretty-date-function
    based off of John Resig's javascript pretty date function.

    NOTE: Only does dates in the past. time argument must be an int.

    @param time int Timestamp in integer.
    @param within_week bool If True, then date will only be pretty-fied within
                             a week. If false, date will always be pretty-fied.
    """
    now = datetime.now()
    #We also check for float since time.time() can give a float timestamp.
    if type(time) is int or type(time) is float:
        time = int(time)
        diff = now - datetime.fromtimestamp(time)
    elif type(time) is datetime:
        diff = now - time
    else: #If our input isn't an int, default to now:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return 'in the future'

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"

    if within_week:
        #We won't continue processing the date.
        return False

    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

#The following needs to go *after* BaseConverter so that the class can be found.
RevisionShortID = BaseConverter(
    #Lowercase and numbers only. We removed the following characters to improve readability for short
    #urls: o, 0 and l, and 1. (26+10) - 4 = 32 characters left. We also
    #randomized the letter-num sequence to make the generated short_ids less
    #guessable.
    #NOTE: Remember to update settings.EXCLUDED_SHORTID_CHARS if you make any
    #      exclusions here.
    'jzt4g58r6fixv3ubqce2w7ykdp9hmasn'
)

def int_to_short(site_id):
    '''
    We want the minimum number of characters for a randomly generated wiki to be
    four. By permutation: 32 * 32 * 32 = 32768, so we add that to our site_id.
    '''
    return RevisionShortID.from_decimal(site_id + 32768)

def short_to_int(short_id):
    '''
    We want the minimum number of characters for a randomly generated wiki to be
    four. By permutation: 32 * 32 * 32 = 32768, so we add that to our site_id.
    '''
    return RevisionShortID.to_decimal(short_id) - 32768
