from django.conf import settings
from django.shortcuts import render_to_response, redirect

from base.models import Wiki 

class SiteTagMiddleware(object):
    '''
    We extract the subdomain part of the url and use that as a unique 'sitetag'.
    '''
    def process_request(self, request):
        '''
        Parse out the subdomain from the request.
        '''
        #For Testing purposes
        if settings.IS_TESTING_WIKI:
            request.base_domain = 'testserver'
            request.subdomain = ''
            settings.WIKI = Wiki.objects.get(tag = 'mywiki')
            request.urlconf = 'wiki.urls'
            return None


        #NOTE: We MUST have the Wiki object stored in a globally accessible
        #      place. So we can't use request.
        settings.WIKI = None #Clear out any persistent setting.

        #Get last two parts and set that as our base domain. No trailing slash.
        host = request.get_host()
        host = host.split('.')
        request.base_domain = '.'.join(host[-2:])
        
        #Check to see if we are currently using a subdomain.
        if len(host) <= 2:
            #Not using a subdomain, so we don't do anything.
            return None

        #Okay, we are using a subdomain. Make sure that there is only one
        #level of subdomain (ie. test.example.com rather than
        #www.test.example.com).
        subdomains = host[:-2] #get everything except base domain
        if len(subdomains) == 1:
            request.subdomain = subdomains[0]
            
            #We need to reprocess the urls here before we get to
            #process_view. Check to see if site exists in DB.
            try:
                settings.WIKI = Wiki.objects.get(tag = request.subdomain)
                #Okay, we are: 1. Using a subdomain and 2. Have a valid wiki
                #associated to that subdomain. So we overwrite our urlconf and
                #load up the wiki!
                request.urlconf = 'wiki.urls'
                return None
            except Wiki.DoesNotExist:
                #We redirect to main page.
                pass
        
        #Otherwise, we aren't dealing with more than one level of subdomain OR
        #wiki doesn't exist. We redirect to main page.
        return redirect('http://'+request.base_domain)
