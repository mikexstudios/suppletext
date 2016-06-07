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

import re
import datetime #for saving two revisions
#import pdb

class WikiLoggedInTest(TestCase):

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
    
    #TODO: Test static for edit page. Other pages.
    def test_static(self):
        r = self.client.get('/static/wiki/css/print.css', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/css/screen.css', {})
        self.assertEqual(r.status_code, 200)
            
        #TODO: Include favicon
        #r = self.client.get('/favicon.ico/', {})
        #self.assertEqual(r.status_code, 302)

    def test_edit_static(self):
        r = self.client.get('/static/wiki/js/markitup/skins/simple/style.css', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/style.css', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/jquery.markitup.js', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/set.js', {})
        self.assertEqual(r.status_code, 200)
        
        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/h1.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/h2.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/h3.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/h4.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/h5.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/bold.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/italic.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/list-bullet.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/list-numeric.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/url.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/picture.png', {})
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/static/wiki/js/markitup/sets/wiki/images/link.png', {})
        self.assertEqual(r.status_code, 200)

    def test_home(self):
        r = self.client.get('/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/HomePage/')
    
    def test_homepage(self):
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['content_html']), u'''<h1>Welcome to your new wiki!</h1>
<p>You will want to replace this text with whatever you want to put on your new home page. This is done by <strong>clicking the "edit this page" link</strong> in the bottom right-hand corner. Any time you want to edit this or any content page, just click on the link!</p>
<p>If you are the <em>administrator</em> of this wiki, you will see a link at the top of this page where you can access the Wiki Admin. There, you will be able to manage users and fine-tune settings for this wiki (like adding a site title)!</p>
<p>Some pages you might want to check out:</p>
<ul><li><a href="/FormattingGuide/">Formatting Guide</a> - read through the simple syntax used to create and edit pages.
</li><li><a href="/SandBox/">SandBox</a> - play around with the syntax here.</li></ul>
''')

    def test_formattingguide(self):
        r = self.client.get('/FormattingGuide/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'FormattingGuide')
        #The FormattingRules guide is too long, so we just match a part of it.
        self.assertNotEqual(re.search(r'<h1>Formatting Guide</h1>', unicode(r.context[-1]['content_html'])), None)

    def test_sandbox(self):
        r = self.client.get('/SandBox/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'SandBox')
        self.assertEqual(unicode(r.context[-1]['content_html']), u'''<h1>SandBox</h1>
<p>Welcome to the Sandbox. This page allows you to carry out experiments, so feel free to do whatever you want here!</p>
<p>To edit, click the <strong>edit link</strong> at the bottom of this page. Then, make your changes in the provided text box, and click the <em>Save Page</em> button when finished. </p>
<p>Be sure to check out the <a href="/FormattingGuide/">formatting guide</a> which will explain what syntax you can use on this wiki. </p>
''')

    def test_unknown(self):
        '''
        Visiting an unknown page.
        '''
        r = self.client.get('/Unknown/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/Unknown:edit/')
    
    def test_unknown_edit(self):
        r = self.client.get('/Unknown:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/edit.html')
    
    def test_unknown_edit_save(self):
        content = 'Default content.'
        r = self.client.post('/Unknown:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Save', })

        #Make sure we are redirected back to HomePage
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/Unknown/')

        #Okay, now make sure homepage has our content.
        r = self.client.get('/Unknown/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'Unknown')
        self.assertEqual(unicode(r.context[-1]['content_html']), 
                         '<p>'+content+"</p>\n")

    def test_homepage_edit(self):
        r = self.client.get('/HomePage:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/edit.html')

    def test_homepage_edit_save(self):
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

    def test_homepage_edit_preview(self):
        content = 'Default content.'
        r = self.client.post('/HomePage:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Preview', })
        
        #Make sure we are at the preview page
        self.assertTemplateUsed(r, 'wiki/preview.html')
        self.assertContains(r, 'Remember that this is only a preview')

    #No content change but with note. Straight save.
    def test_homepage_edit_save_note(self):
        content = 'Default content.'
        r = self.client.post('/HomePage:edit/', 
                             {'note': 'This is a note.', 
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

    # Preview -> Save with note.
    def test_homepage_edit_preview_note(self):
        content = 'Default content.'
        r = self.client.post('/HomePage:edit/', 
                             {'note': 'This is a note.', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Save', 
                              'from': 'Preview'}) #the only difference

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

    #Wipe everything.
    def test_homepage_edit_wipe(self):
        r = self.client.post('/HomePage:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': '', 
                              'edit': 'default', 
                              'time': '2010-03-03 14:13:00', 
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
                         u'') #empty content

    #Test other pages that depend on more than one revision
    def _setup_homepage_two_revisions(self):
        r = self.client.post('/HomePage:edit/', 
                             {'note': 'Added greeting.', 
                              'view': 'default', 
                              'content': 'Hello, world!', 
                              'edit': 'default', 
                              'time': '2010-03-03 20:44:24', 
                              'action': 'Save', })
        self.assertEqual(r.status_code, 302) 
        self.assertEquals(r['Location'], 'http://testserver/HomePage/')
        
        #Since the prevous page and current page saves almost immediately,
        #we need to set the time of current save to the future a bit.
        now = datetime.datetime.now()
        now += datetime.timedelta(minutes = 1) #add 1 min to now
        now = str(now).split('.')[0] #discard microseconds part

        r = self.client.post('/HomePage:edit/', 
                             {'note': 'Changed greeting.', 
                              'view': 'default', 
                              'content': 'Goodbye, world! Goodnight!', 
                              'edit': 'default', 
                              'time': now,
                              #'time': '2010-03-03 20:45:41', 
                              'action': 'Save', })
        self.assertEqual(r.status_code, 302) 
        self.assertEquals(r['Location'], 'http://testserver/HomePage/')
    
    def test_homepage_history(self):
        self._setup_homepage_two_revisions()

        r = self.client.get('/HomePage:history/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/history.html')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['history']), u'[<Page: HomePage>, <Page: HomePage>]')
        self.assertContains(r, 'Added greeting.', 1)
        self.assertContains(r, 'Changed greeting.', 1)
    
    def test_homepage_view_revisions(self):
        self._setup_homepage_two_revisions()

        r = self.client.get('/HomePage:show/zjjg/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/show.html')
        self.assertEqual(unicode(r.context[-1]['rev']), u'4')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['content_html']), u"<p>Hello, world!</p>\n")
        self.assertContains(r, 'Added greeting.', 1)
        
        r = self.client.get('/HomePage:show/zjj5/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/show.html')
        self.assertEqual(unicode(r.context[-1]['rev']), u'5')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['content_html']), u"<p>Goodbye, world! Goodnight!</p>\n")
        self.assertContains(r, 'Changed greeting.', 1)
    
    def test_homepage_compare_revisions(self):
        self._setup_homepage_two_revisions()
        
        r = self.client.get('/HomePage:compare/zjj5/zjjg/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/compare.html')
        self.assertEqual(unicode(r.context[-1]['page_b']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['diffs']), u"[({'base': {'start': 1, 'total_lines': 1}, 'changed': {'start': 1, 'total_lines': 1}}, [{'base': {'lines': [u'<del>Hello, world</del>!'], 'offset': 0}, 'type': 'mod', 'changed': {'lines': [u'<ins>Goodbye, world! Goodnight</ins>!'], 'offset': 0}}])]")
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertContains(r, 'Changed greeting.', 1)
    
    def test_homepage_revert_to_first_revision(self):
        self._setup_homepage_two_revisions()

        r = self.client.get('/HomePage:revert/zjjg/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/HomePage/')
        
        #Verify on our HomePage that the change has occured.
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/show.html')
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['content_html']), u"<p>Hello, world!</p>\n")

        #Check that the history has one more entry.
        r = self.client.get('/HomePage:history/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertEqual(unicode(r.context[-1]['history']), u'[<Page: HomePage>, <Page: HomePage>, <Page: HomePage>]')
        self.assertContains(r, 'Added greeting.', 1)
        self.assertContains(r, 'Changed greeting.', 1)
        self.assertContains(r, 'Reverted to revision zjjg.', 1)

    def test_userbox_homepage(self):
        '''When logged in, userbox should appear on HomePage.'''
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertContains(r, 'Wiki Admin', 2) #once in userbox, once in body
        self.assertContains(r, 'Logout', 1)


class WikiLoggedOutTest(WikiLoggedInTest):
    '''
    We are anonymous user. All pages have default permissions.

    NOTE: We inherit from the logged in test cases. Anything that we think
          should be different should be overridden here.
    '''

    def setUp(self):
        super(WikiLoggedOutTest, self).setUp()

        self.client.logout()

    def test_unknown(self):
        '''
        Visiting an unknown page.
        '''
        r = self.client.get('/Unknown/', {})
        self.assertEqual(r.status_code, 302)
        self.assertEquals(r['Location'], 'http://testserver/Unknown:edit/')
        
        r = self.client.get('/Unknown:edit/', {})
        self.assertEqual(r.status_code, 200)
        #Make sure we are showing the premission required page.
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/Unknown:edit/'}")
    
    def test_unknown_edit(self):
        '''
        Since user doesn't have edit perm, we expect a perm required page.
        '''
        r = self.client.get('/Unknown:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/Unknown:edit/'}")
    
    def test_unknown_edit_save(self):
        '''
        Since user doesn't have edit perm, we expect a perm required page.
        '''
        content = 'Default content.'
        r = self.client.post('/Unknown:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Save', })
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/Unknown:edit/'}")


    def test_homepage_edit(self):
        r = self.client.get('/HomePage:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:edit/'}")

    def test_homepage_edit_save(self):
        content = 'Default content.'
        r = self.client.post('/HomePage:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Save', })
        #Should get to perm required page.
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:edit/'}")

    def test_homepage_edit_preview(self):
        content = 'Default content.'
        r = self.client.post('/HomePage:edit/', 
                             {'note': '', 
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': '2010-03-03 14:01:36', 
                              'action': 'Preview', })
        
        #Should get to perm required page.
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:edit/'}")
   
    #We won't test these because we anything involving editing while logged out,
    #we already tested.
    def test_homepage_edit_preview_note(self):
        pass
    def test_homepage_edit_save_note(self):
        pass
    def test_homepage_edit_wipe(self):
        pass


    #Other functionality pages:
    def _setup_homepage_two_revisions(self):
        self.assertTrue(self.client.login(username = 'test', password = 'test'))
        super(WikiLoggedOutTest, self)._setup_homepage_two_revisions()
        self.client.logout()
    
    def test_homepage_revert_to_first_revision(self):
        self._setup_homepage_two_revisions()

        r = self.client.get('/HomePage:revert/zjjg/', {})
        #Instead of redirecting, we'll see perm required page.
        self.assertEqual(r.status_code, 200) 
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'edit')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage:revert/zjjg/'}")
    
    
    def test_userbox_homepage(self):
        '''When logged in, userbox should not appear on HomePage.'''
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertContains(r, 'Wiki Admin', 1) #once in body only
        self.assertNotContains(r, 'Logout')


class WikiNonAdminLoggedInTest(WikiLoggedInTest):
    '''
    We are just a logged in user, not admin. We are assuming default wiki
    permissions: read -> anyone; edit -> logged in; special -> contributor.

    NOTE: We inherit from the logged in test cases. Anything that we think
          should be different should be overridden here.
    '''

    def setUp(self):
        super(WikiNonAdminLoggedInTest, self).setUp()
        #Logout from 'test' user (admin).
        self.client.logout()
        #Create and login to 'test2' user (a regular logged in user).
        User.objects.create_user('test2', 'test2@example.com', 'test2')
        self.assertTrue(self.client.login(username = 'test2', password = 'test2'))
    

    def test_userbox_homepage(self):
        '''When logged in, userbox should appear on HomePage.'''
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        #Since we are NOT admin, we shouldn't see the Wiki Admin in the userbox
        #at top of page.
        self.assertContains(r, 'Wiki Admin', 1) #once in userbox
        self.assertContains(r, 'Logout', 1)


class WikiChangePagePermTest(TestCase):

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

        #Create a HomePage so that settings can be set.
        w = Wiki.objects.get(tag = 'mywiki')
        p = Page()
        p.wiki = w
        p.tag = 'HomePage'
        p.content = 'Welcome to your new wiki!'
        p.ip_address = '127.0.0.1'
        p.save()

    def test_homepage_permissions_nonexistant_perm(self):
        r = self.client.post('/HomePage:permissions/', {'view': 'unknown', })
        self.assertEqual(r.status_code, 404)
        
        r = self.client.post('/HomePage:permissions/', {'edit': 'unknown', })
        self.assertEqual(r.status_code, 404)

        #Also test passing in unknown keys:
        r = self.client.post('/HomePage:permissions/', {'special': 'anyone', })
        self.assertEqual(r.status_code, 404)
    
    def test_nonexistant_page_permissions(self):
        r = self.client.post('/Unknown:permissions/', {'view': 'unknown', })
        self.assertEqual(r.status_code, 404)
        
        r = self.client.post('/Unknown:permissions/', {'edit': 'unknown', })
        self.assertEqual(r.status_code, 404)

        #Also test passing in unknown keys:
        r = self.client.post('/Unknown:permissions/', {'special': 'anyone', })
        self.assertEqual(r.status_code, 404)

    def test_homepage_permissions_view_loggedin(self):
        r = self.client.post('/HomePage:permissions/', {'view': 'loggedin', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'success', 1)

        self.client.logout()

        #Now as our second anonymous user try to access HomePage
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/perm_required.html')
        self.assertEqual(unicode(r.context[-1]['required_role']), u'loggedin')
        self.assertEqual(unicode(r.context[-1]['intended_action']), u'view')
        self.assertEqual(unicode(r.context[-1]['extra']), u"{'next': u'http://testserver/HomePage/'}")
        
        #Create and login second user.
        User.objects.create_user('test2', 'test2@example.com', 'test2')
        self.assertTrue(self.client.login(username = 'test2', password = 'test2'))

        #We should be able to view the page.
        r = self.client.get('/HomePage/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/show.html')
        self.assertEqual(unicode(r.context[-1]['rev']), u'None')
        self.assertEqual(unicode(r.context[-1]['page']), u'HomePage')
        self.assertContains(r, 'Welcome to your new wiki!', 1)
    
    def test_homepage_permissions_edit_anyone(self):
        r = self.client.post('/HomePage:permissions/', {'edit': 'anyone', })
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'success', 1)

        self.client.logout()
        
        #We should be able to view the edit page and save to it.
        r = self.client.get('/HomePage:edit/', {})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'wiki/edit.html')

        content = 'Default content.'
        #Since the prevous page and current page saves almost immediately,
        #we need to set the time of current save to the future a bit.
        now = datetime.datetime.now()
        now += datetime.timedelta(minutes = 1) #add 1 min to now
        now = str(now).split('.')[0] #discard microseconds part
        r = self.client.post('/HomePage:edit/', 
                             {'note': '', 
                              #having perms mixed in here shouldn't matter since
                              #we aren't posting to :permissions/
                              'view': 'default', 
                              'content': content,
                              'edit': 'default', 
                              'time': now, 
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
