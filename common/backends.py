from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from wiki.models import Page
from base.models import Wiki, Membership

#We use bitwise permissions. See:
#http://noehr.org/2009/08/27/bitwise-permissions-in-python-and-django/
#Here are our roles. We don't store the bitwise permissions in the database.
#Rather, we store the permission labels.
ROLES = {}
ROLES['anyone'] = 1 << 0
ROLES['loggedin'] = ROLES['anyone'] | 1 << 1
ROLES['contributor'] = ROLES['loggedin'] | 1 << 2
#We set administrator bit higher since it's our highest role.
ROLES['administrator'] = ROLES['contributor'] | 1 << 8

class WikiPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        return None #skip to next auth backend

    def has_perm(self, user, perm, page = None):
        #We only handle objects of type Page. 
        if page is None or not isinstance(page, Page):
            return False
        
        #Get the latter part of the permission (ie. 'model.can_perm' -> 
        #'can_perm'); then get the 'perm' part.
        try:
            perm = perm.split('.')[-1].split('_')[1]
        except IndexError:
            return False
        
        #We figure out what group the user belongs to. We also specifically
        #check for AnonymousUser here.
        if user.is_authenticated():
            try:
                user_group = Membership.objects.get(wiki = page.wiki, user = user)
                #Means that user is either contributor or administrator.
                user_group = user_group.permission
            except Membership.DoesNotExist:
                #User isn't a member of the wiki but is logged in.
                user_group = 'loggedin'
        else:
            user_group = 'anyone'

        #Now given the group, determine what the user can do. First, we get
        #global permissions for the wiki.
        page_group = getattr(page.wiki, 'default_%s' % perm)
        #Then we see if the page has specific permissions set.
        temp = getattr(page, 'can_%s' % perm, False)
        if temp:
            page_group = temp

        #Now figure out if the user's group is the same or a superset of the page
        #permission. We use bitwise permissions.
        user_group_bit = ROLES[user_group]
        page_group_bit = ROLES[page_group]
        #We want the user_group_bit to contain all page_group_bits. AND gives the
        #bits that both have in common. So we take the common bits and compare them
        #to page_group_bit. 
        if (user_group_bit & page_group_bit) == page_group_bit:
            #User has access.
            return True
        #Otherwise, user is not in a group that has access. We return False but
        #set in the user object a role that is required.
        #(Helps with our perm_required.html page).
        user.required_role = page_group
        return False

class WikiAdminPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        return None #skip to next auth backend

    def has_perm(self, user, perm, wiki = None):
        #We only handle object permissions and only objects of Wiki. 
        if wiki is None or not isinstance(wiki, Wiki):
            return False 
        
        #Get the latter part of the permission (ie. 'model.can_perm' -> 
        #'can_perm'); then get the 'perm' part.
        try:
            perm = perm.split('.')[-1].split('_')[1]
        except IndexError:
            return False

        #We only handle the admin action for now.
        if perm != 'admin':
            raise Exception('perm must be can_admin')
        
        #We figure out what group the user belongs to. We also specifically
        #check for AnonymousUser here.
        if user.is_authenticated():
            try:
                user_group = Membership.objects.get(wiki = wiki, user = user)
                #Means that user is either contributor or administrator.
                user_group = user_group.permission
            except Membership.DoesNotExist:
                #User isn't a member of the wiki but is logged in.
                user_group = 'loggedin'
        else:
            user_group = 'anyone'

        #User must be admin to access the admin area:
        if user_group == 'administrator':
            return True

        #Otherwise, user is not in a group that has access. We return False but
        #set in the user object a role that is required.
        #(Helps with our perm_required.html page).
        user.required_role = 'administrator'
        return False
