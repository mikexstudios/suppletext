from django.db import models
from django.contrib.auth.models import User

class Wiki(models.Model):
    #id is auto-defined and is auto-incrementing
    created = models.DateTimeField(auto_now_add = True)
    #TODO: Maybe change to slug field.
    tag = models.CharField(blank = True, max_length = 50)
    
    name = models.CharField(blank = True, max_length = 60)
    tagline = models.CharField(blank = True, max_length = 140)
    front_page = models.CharField(max_length = 100, default = 'HomePage')

    default_view = models.CharField(max_length = 15, default = 'anyone')
    default_edit = models.CharField(max_length = 15, default = 'loggedin')
    default_special = models.CharField(max_length = 15, default = 'contributor')

    members = models.ManyToManyField(User, through = 'Membership')
    
    def __unicode__(self):
        return self.tag

#We use the Membership model to add extra information for the many-to-many
#relationship. See: http://docs.djangoproject.com/en/1.1/topics/db/
#models/#extra-fields-on-many-to-many-relationships
class Membership(models.Model):
    user = models.ForeignKey(User)
    wiki = models.ForeignKey(Wiki)
    permission = models.CharField(max_length = 30)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    name = models.CharField(max_length = 60) #maybe increase to 255?
    website = models.URLField()
#Sort-of hackish post-save signal. The purpose is to hook on to the save() of
#User objects to make sure that the UserProfile is created. BUT the profile is that
#this is called every time we save (which isn't a lot).
def user_post_save(sender, instance, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)
models.signals.post_save.connect(user_post_save, User)

