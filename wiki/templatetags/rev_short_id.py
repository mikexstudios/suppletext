from django import template
#from django.conf import settings

from wiki.helpers import int_to_short

register = template.Library()

def rev_short_id(int_id, arg=None):
    '''
    Given an int, returns the corresponding short ID.
    '''
    if not int_id:
        return u''

    try:
        int_id = int(int_id)
    except ValueError:
        #Means that the int_id wasn't an int.
        return u''
    
    return int_to_short(int_id)
register.filter('rev_short_id', rev_short_id)
    
