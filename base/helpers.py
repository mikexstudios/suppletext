from django.conf import settings 
from django.shortcuts import render_to_response

from datetime import datetime

import urllib, hashlib

def context_processor(request):
    '''
    Not called directly, but used by django's context_processor.
    Remember: Add this function in settings.

    NOTE: CURRENTLY NOT USED!
    '''
    return {
        'base_url': 'http://'+request.META['HTTP_HOST'],
        'media_path': settings.MEDIA_URL.rstrip('/'),
        'wiki_media_path': settings.WIKI_MEDIA_URL.rstrip('/'),
        'base_media_path': settings.BASE_MEDIA_URL.rstrip('/'),
        'wiki_admin_media_path': settings.WIKI_ADMIN_MEDIA_URL.rstrip('/'),
    }

def get_gravatar_link(email, size = 64): #in px
    default = 'identicon'
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(email).hexdigest(), 
                                      'default':default, 'size':str(size)})
    return gravatar_url
    

def user_auth_active(user):
    '''
    Used in decorator @user_passes_test to check if user is both authenticated
    and is active.
    '''
    return user.is_authenticated() and user.is_active

#TODO: Remove this.
#def pretty_date(time = False, within_week = True):
#    """
#    Get a datetime object or a int() Epoch timestamp and return a
#    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
#    'just now', etc
#
#    Written by: http://evaisse.com/post/93417709/python-pretty-date-function
#    based off of John Resig's javascript pretty date function.
#
#    NOTE: Only does dates in the past. time argument must be an int.
#
#    @param time int Timestamp in integer.
#    @param within_week bool If True, then date will only be pretty-fied within
#                             a week. If false, date will always be pretty-fied.
#    """
#    now = datetime.now()
#    #We also check for float since time.time() can give a float timestamp.
#    if type(time) is int or type(time) is float:
#        time = int(time)
#        diff = now - datetime.fromtimestamp(time)
#    elif type(time) is datetime:
#        diff = now - time
#    else: #If our input isn't an int, default to now:
#        diff = now - now
#    second_diff = diff.seconds
#    day_diff = diff.days
#
#    if day_diff < 0:
#        return 'in the future'
#
#    if day_diff == 0:
#        if second_diff < 10:
#            return "just now"
#        if second_diff < 60:
#            return str(second_diff) + " seconds ago"
#        if second_diff < 120:
#            return  "a minute ago"
#        if second_diff < 3600:
#            return str( second_diff / 60 ) + " minutes ago"
#        if second_diff < 7200:
#            return "an hour ago"
#        if second_diff < 86400:
#            return str( second_diff / 3600 ) + " hours ago"
#    if day_diff == 1:
#        return "Yesterday"
#    if day_diff < 7:
#        return str(day_diff) + " days ago"
#
#    if within_week:
#        #We won't continue processing the date.
#        return False
#
#    if day_diff < 31:
#        return str(day_diff/7) + " weeks ago"
#    if day_diff < 365:
#        return str(day_diff/30) + " months ago"
#    return str(day_diff/365) + " years ago"


"""
Convert numbers from base 10 integers to base X strings and back again.

Original: http://www.djangosnippets.org/snippets/1431/

Sample usage:

>>> base20 = BaseConverter('0123456789abcdefghij')
>>> base20.from_decimal(1234)
'31e'
>>> base20.to_decimal('31e')
1234
"""
class BaseConverter(object):
    decimal_digits = "0123456789"
    
    def __init__(self, digits):
        self.digits = digits
    
    def from_decimal(self, i):
        return self.convert(i, self.decimal_digits, self.digits)
    
    def to_decimal(self, s):
        return int(self.convert(s, self.digits, self.decimal_digits))
    
    def convert(number, fromdigits, todigits):
        # Based on http://code.activestate.com/recipes/111286/
        if str(number)[0] == '-':
            number = str(number)[1:]
            neg = 1
        else:
            neg = 0

        # make an integer out of the number
        x = 0
        for digit in str(number):
           x = x * len(fromdigits) + fromdigits.index(digit)
    
        # create the result in base 'len(todigits)'
        if x == 0:
            res = todigits[0]
        else:
            res = ""
            while x > 0:
                digit = x % len(todigits)
                res = todigits[digit] + res
                x = int(x / len(todigits))
            if neg:
                res = '-' + res
        return res
    convert = staticmethod(convert)

#The following needs to go *after* BaseConverter so that the class can be found.
ShortID = BaseConverter(
    #Lowercase and numbers only. We removed the following characters to improve readability for short
    #urls: o, 0 and l, and 1. (26+10) - 4 = 32 characters left. We also
    #randomized the letter-num sequence to make the generated short_ids less
    #guessable.
    #NOTE: Remember to update settings.EXCLUDED_SHORTID_CHARS if you make any
    #      exclusions here.
    'mwczh7erqnf6v2ay43k9gtbju5sp8idx'
)

def wiki_id_to_short_id(site_id):
    '''
    We want the minimum number of characters for a randomly generated wiki to be
    four. By permutation: 32 * 32 * 32 = 32768, so we add that to our site_id.
    '''
    return ShortID.from_decimal(site_id + 32768)

def short_id_to_wiki_id(short_id):
    '''
    We want the minimum number of characters for a randomly generated wiki to be
    four. By permutation: 32 * 32 * 32 = 32768, so we add that to our site_id.
    '''
    return ShortID.to_decimal(short_id) - 32768
