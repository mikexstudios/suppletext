from django.test import TestCase
from django.test.client import Client
#import test_utils.utils.twill_runner as twill
#from twill.commands import TwillAssertionError
#from BeautifulSoup import BeautifulSoup
#from StringIO import StringIO #to make twill quiet

from django.contrib.auth.models import User

class BaseTest(TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    #def test_favicon(self):
    #    r = self.client.get('/favicon.ico/', {})
    #    #Right now, we don't have one.
    #    self.assertEqual(r.status_code, 404)
    
    def test_home(self):
        r = self.client.get('/', {})
        self.assertEqual(r.status_code, 200)
   
    def test_home_static(self):
        r = self.client.get('/static/base/css/screen.css', {})
        self.assertEqual(r.status_code, 200)
        
        r = self.client.get('/static/base/css/print.css', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/combined_screenshot_700x220.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/fancy-button/shade.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/features/lessismore.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/features/wikicreole.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/features/signin.png', {})
        self.assertEqual(r.status_code, 200)
        
        r = self.client.get('/static/base/images/features/diff.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/features/controlpanel.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/features/pageperm.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/features/feedback.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/base/images/fancy-button/border_1000x200.png', {})
        self.assertEqual(r.status_code, 200)
    
    def test_signup(self):
        r = self.client.get('/signup/', {})
        self.assertEqual(r.status_code, 200)
        #Make sure the login page is displayed
        self.assertTemplateUsed(r, 'base/signup_step1.html')

        #Now fake our login. We need to create a user first. We will completely
        #bypass our django_rpx_plus system since that will make our tests a lot more
        #complex.
        User.objects.create_user('test', 'test@example.com', 'test')
        self.assertTrue(self.client.login(username = 'test', password = 'test'))

        #Visit signup again and make sure we get to step 2:
        r = self.client.get('/signup/', {})
        self.assertEqual(r.status_code, 200)
        #Make sure the login page is displayed
        self.assertTemplateUsed(r, 'base/signup_step2.html')

        #Now create a wiki:
        r = self.client.post('/signup/', 
                             {'subdomain': 'mywiki', 
                              #'submit': 'Claim', 
                              'title': 'My Excellent Wiki',})
        self.failUnlessEqual(r.status_code, 302) #redirect

        #We can't check final path of redirect since our subdomain hack doesn't
        #play well with tests.


class ProfileTest(TestCase):

    def setUp(self):
        #Create test user and login.
        User.objects.create_user('test', 'test@example.com', 'test')
        self.assertTrue(self.client.login(username = 'test', password = 'test'))

    def tearDown(self):
        pass
    
    def test_nonexistant_user_page(self):
        r = self.client.get('/user/unknown/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/')

    def test_user_page_loggedout(self):
        self.client.logout()

        r = self.client.get('/user/test/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['profile']), u'test')
        self.assertNotContains(r, 'edit profile')
    
    def test_user_page_loggedin(self):
        r = self.client.get('/user/test/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['profile']), u'test')
        self.assertContains(r, 'edit profile', 1)

    def test_profile(self):
        r = self.client.get('/accounts/profile/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'base/change_profile.html')
        #We can't check for number of logins string because we didn't create
        #user through RPX. This test user has 0 logins associated with acct.
        self.assertContains(r, 'This is what people will see on your', 1)
    
    def test_change_profile(self):
        website = 'http://www.test.com/'
        name = 'First Last'
        email = 'test@test.com'
        r = self.client.post('/accounts/profile/', 
                             {'website': website, 
                              'name': name, 
                              'submit': 'Save', 
                              'email': email, })
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'base/change_profile.html')
        self.assertContains(r, 'Your profile was successfully updated.', 1)

        #Make sure the user profile actually changed.
        u = User.objects.get(username = 'test')
        self.assertEqual(u.email, email)
        self.assertEqual(u.get_profile().name, name)
        self.assertEqual(u.get_profile().website, website)

        #Now make sure the changes are displayed on the user's profile page.
        r = self.client.get('/user/test/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['profile']), u'test')
        self.assertContains(r, name, 1)
        self.assertContains(r, website, 1)

