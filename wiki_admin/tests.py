from django.test import TestCase
from django.test.client import Client
#import test_utils.utils.twill_runner as twill
#from twill.commands import TwillAssertionError
#from BeautifulSoup import BeautifulSoup
#from StringIO import StringIO #to make twill quiet

from django.conf import settings
from django.contrib.auth.models import User
from base.models import Wiki 
from wiki.models import Page

#import re
#import pdb

class WikiAdminLoggedInTest(TestCase):

    def setUp(self):
        #Settings are kept in between tests, so we need to reset this:
        settings.IS_TESTING_WIKI = False
        #Make sure we create a user and sign up for a wiki first.
        User.objects.create_user('test', 'test@example.com', 'test')
        self.assertTrue(self.client.login(username = 'test', password = 'test'))
        #Now create a wiki:
        r = self.client.post('/signup/', 
                             {'subdomain': 'mywiki', 
                              #'submit': 'Claim', 
                              'title': 'My Excellent Wiki',})
        self.failUnlessEqual(r.status_code, 302) #redirect

        #Now we force the middleware to pretend that we're in a subdomain.
        settings.IS_TESTING_WIKI = True

    def tearDown(self):
        pass
    
    def test_home(self):
        r = self.client.get('/admin/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/admin/settings/')

    def test_settings(self):
        r = self.client.get('/admin/settings/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki_admin/settings.html')
        self.assertContains(r, 'General Site', 1)
        self.assertContains(r, 'Default Permissions', 1)

    def test_settings_change_name_tagline(self):
        #First ascertain our default values
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.name, 'My Excellent Wiki')
        self.assertEqual(w.tagline, '')

        r = self.client.post('/admin/settings/', 
                             {'name': 'My Cool Wiki', 
                              'default_edit': 'loggedin', 
                              'default_view': 'anyone', 
                              'default_special': 'contributor', 
                              'tagline': 'Some text here.', 
                              'front_page': 'HomePage', 
                              'submit': 'Save', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Settings was successfully updated.', 1)

        #Now make sure our changes are reflected in db
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.name, 'My Cool Wiki')
        self.assertEqual(w.tagline, 'Some text here.')

    def test_settings_change_frontpage(self):
        #First ascertain our default values
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.front_page, 'HomePage')

        r = self.client.post('/admin/settings/', 
                             {'name': 'My Excellent Wiki', 
                              'default_edit': 'loggedin', 
                              'default_view': 'anyone', 
                              'default_special': 'contributor', 
                              'tagline': '', 
                              'front_page': 'SandBox', 
                              'submit': 'Save', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Settings was successfully updated.', 1)

        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.front_page, 'SandBox')

        #Confirm by actually visiting
        r = self.client.get('/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/SandBox/')

    def test_settings_change_frontpage_nonexistant(self):
        #First ascertain our default values
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.front_page, 'HomePage')

        r = self.client.post('/admin/settings/', 
                             {'name': 'My Excellent Wiki', 
                              'default_edit': 'loggedin', 
                              'default_view': 'anyone', 
                              'default_special': 'contributor', 
                              'tagline': '', 
                              'front_page': 'Unknown', 
                              'submit': 'Save', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Settings was successfully updated.', 1)

        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.front_page, 'Unknown')

        #Confirm by actually visiting
        r = self.client.get('/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/Unknown/')

        #Then it redirects to Unknown:edit, but we don't need to check that.
    
    #We need the following for our permission tests:
    def _setup_second_user(self):
        User.objects.create_user('test2', 'test2@example.com', 'test2')
    def _login_first_user(self):
        self.assertTrue(self.client.login(username = 'test', password = 'test'))
    def _login_second_user(self):
        self.assertTrue(self.client.login(username = 'test2', password = 'test2'))


    def test_settings_change_rw_anyone(self):
        '''
        Read: anyone; Write: anyone
        '''
        #Check default
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.default_view, 'anyone')
        self.assertEqual(w.default_edit, 'loggedin')

        r = self.client.post('/admin/settings/', 
                             {'name': 'My Excellent Wiki', 
                              'default_edit': 'anyone', 
                              'default_view': 'anyone', 
                              'default_special': 'contributor', 
                              'tagline': '', 
                              'front_page': 'HomePage', 
                              'submit': 'Save', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Settings was successfully updated.', 1)
        
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.default_view, 'anyone')
        self.assertEqual(w.default_edit, 'anyone')
        
        #Now as the second user (anonymous)
        self.client.logout()
        
        #We expect to be able to view the edit page.
        r = self.client.get('/HomePage:edit/', {})
        self.assertEqual(r.status_code, 200)
        #Technically, we shouldn't be getting page_perm form since that's 
        #contributors only. But the code right now sends it anyway, but doesn't
        #show it when template renders.
        #self.assertEqual(unicode(r.context[-1]['page_permissions_form']), None)
        self.assertEqual(unicode(r.context[-1]['page_tag']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        
        #We also expect to have edits saved.
        content = 'Default content.'
        r = self.client.post('/HomePage:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Save', })

        #Make sure we are redirected back to HomePage
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/HomePage/')

        #Okay, now make sure homepage has our content.
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['content_html']), 
                         '<p>'+content+"</p>\n")

    def test_settings_change_rw_loggedin(self):
        '''
        Read: loggedin; Write: loggedin
        '''
        #Check default
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.default_view, 'anyone')
        self.assertEqual(w.default_edit, 'loggedin')

        r = self.client.post('/admin/settings/', 
                             {'name': 'My Excellent Wiki', 
                              'default_edit': 'loggedin', 
                              'default_view': 'loggedin', 
                              'default_special': 'contributor', 
                              'tagline': '', 
                              'front_page': 'HomePage', 
                              'submit': 'Save', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Settings was successfully updated.', 1)
        
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.default_view, 'loggedin')
        self.assertEqual(w.default_edit, 'loggedin')
        
        #Now as the second user (anonymous)
        self.client.logout()
        
        #We check a few pages, but we shouldn't be able to view them.
        #TODO: Make each of these its own test.
        #TODO: Test more pages like show a specific revision.
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'view')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage/'}")
    
        r = self.client.get('/HomePage:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:edit/'}")
    
        r = self.client.get('/HomePage:history/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'view')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:history/'}")

        r = self.client.get('/HomePage:compare/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'view')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:compare/'}")

        r = self.client.get('/HomePage:revert/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'view')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:revert/'}")
        
        r = self.client.get('/HomePage:permissions/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'contributor')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'special')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:permissions/'}")
        
        #Now log second user in and just test HomePage. We assume that permissions
        #are probably correct and enforcing them was checked in WikiLoggedInTest.
        self._setup_second_user()
        self._login_second_user()

        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/show.html')
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        
        r = self.client.get('/HomePage:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/edit.html')
        
        content = 'Default content.'
        r = self.client.post('/HomePage:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Save', })

        #Make sure we are redirected back to HomePage
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/HomePage/')

        #Okay, now make sure homepage has our content.
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['content_html']), 
                         '<p>'+content+"</p>\n")


    def test_settings_change_rw_contributor(self):
        '''
        Read: contributor; Write: contributor
        '''
        #Check default
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.default_view, 'anyone')
        self.assertEqual(w.default_edit, 'loggedin')

        r = self.client.post('/admin/settings/', 
                             {'name': 'My Excellent Wiki', 
                              'default_edit': 'contributor', 
                              'default_view': 'contributor', 
                              'default_special': 'contributor', 
                              'tagline': '', 
                              'front_page': 'HomePage', 
                              'submit': 'Save', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Settings was successfully updated.', 1)
        
        w = Wiki.objects.get(tag = 'mywiki')
        self.assertEqual(w.default_view, 'contributor')
        self.assertEqual(w.default_edit, 'contributor')
        
        #Now log second user in and just test HomePage. We assume that permissions
        #are probably correct and enforcing them was checked in WikiLoggedInTest.
        self.client.logout()
        self._setup_second_user()
        self._login_second_user()
        
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'contributor')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'view')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage/'}")
    
        r = self.client.get('/HomePage:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['required_role']), u'contributor')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:edit/'}")

    def test_users(self):
        r = self.client.get('/admin/users/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki_admin/users.html')
        self.assertContains(r, 'Manage Users', 1)
        self.assertContains(r, 'Add User') #there are multiple instances

    def test_users_static_jqueryconfirm(self):
        '''Required for users settings page.'''
        r = self.client.get('/static/wiki_admin/js/jquery.confirm-1.2.js', {})
        self.assertEqual(r.status_code, 200)

    def test_users_add_nonexistant_user(self):
        r = self.client.post('/admin/users/', 
                             {'username': 'Unknown', 
                              'user_role': 'contributor', 
                              'submit': 'Add User', })
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki_admin/users.html')
        #Check for error
        self.assertContains(r, 'Please correct the error below.', 1)
        self.assertContains(r, 'The user you are adding does not exist!', 1)
        #TODO: Can also check on the database/code side.

    def test_users_add_test2_user(self):
        #Create user first
        self._setup_second_user()

        r = self.client.post('/admin/users/', 
                             {'username': 'test2', 
                              'user_role': 'contributor', 
                              'submit': 'Add User', })
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki_admin/users.html')
        #Check for success
        self.assertContains(r, 'Users was successfully added.', 1)
        self.assertContains(r, 'test2') #multiple instances
    
    def test_users_remove_nonexistant_user(self):
        r = self.client.get('/admin/users/delete/unknown/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/admin/users/')
        
        #messages var not set, we need to peek into the context of the next page.
        r = self.client.get('/admin/users/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki_admin/users.html')
        self.assertContains(r, 'The user you are trying to delete does not exist.', 1)
    
    def test_users_remove_self(self):
        r = self.client.get('/admin/users/delete/test/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/admin/users/')
        
        #messages var not set, we need to peek into the context of the next page.
        r = self.client.get('/admin/users/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki_admin/users.html')
        self.assertContains(r, 'Nice try, but you shouldn&#39;t delete yourself!', 1)




