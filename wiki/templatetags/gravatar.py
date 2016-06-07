from django import template
#from django.conf import settings

from base.helpers import get_gravatar_link

register = template.Library()

def gravatar_img(email, arg=32): #px
    '''
    Given an email address, returns a gravatar img url.
    '''
    if not email:
        return u''

    try:
        size = int(arg)
    except ValueError:
        #Means that the arg wasn't just an int.
        size = 32 #px
    
    return get_gravatar_link(email, size)
register.filter('gravatar_img', gravatar_img)
    
