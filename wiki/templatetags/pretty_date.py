from django import template
from django.conf import settings
from django.utils.dateformat import format

from wiki.helpers import pretty_date

register = template.Library()

def pretty_date_filter(value, arg=None):
    '''
    Formats a date trying to be pretty, but if date is over a month ago,
    then fall back on django's default date formatter.
    '''
    if not value:
        return u''
    if arg is None:
        arg = settings.DATE_FORMAT
    try:
        #Run the date through pretty_date first...
        formatted = pretty_date(value)
        #REMOVE BELOW: pretty_date always outputs pretty date so below doesn't apply.
        if formatted == False:
            #Means we are over a week in time difference, format using django
            #date.
            return format(value, arg)
        #Otherwise...
        return formatted
    except AttributeError:
        return ''

register.filter('pretty_date', pretty_date_filter)
    
