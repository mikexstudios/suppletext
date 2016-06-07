from django.db import models
from django.contrib.auth.models import User

class Page(models.Model):
    #id is auto-defined and is auto-incrementing
    wiki = models.ForeignKey('base.Wiki')
    tag = models.CharField(max_length = 100)
    created = models.DateTimeField(auto_now_add = True)
    #updated = models.DateTimeField(auto_now = True)
    #We let null be true for AnonymousUser object. Should blank = True?
    author = models.ForeignKey(User, null = True)
    ip_address = models.IPAddressField()
    content = models.TextField(blank = True)
    note = models.CharField(blank = True, max_length = 300)
    
    #Allowed values can be found in settings.PERMISSION_CHOICES. If blank,
    #will use default perm.
    #IDEA: We might want to use hard-coded integer values instead of text
    #      labels for better speed. We can match the integers with the
    #      settings tuple. Problem is, we need to keep the settings tuple
    #      order fixed, which may not be very flexible.
    can_view = models.CharField(blank = True, max_length = 30)
    can_edit = models.CharField(blank = True, max_length = 30)
    can_special = models.CharField(blank = True, max_length = 30)

    def __unicode__(self):
        return self.tag
