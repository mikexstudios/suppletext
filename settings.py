# Django settings for suppletext project.
import os
import django
import sys
import re #for SEARCH_HEADER regex

# For setting relative paths. See: http://tinyurl.com/adsa3k
# Path of Django framework files (no trailing /):
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
# Path of this "site" (no trailing /):
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'suppletext'             # Or path to database file if using sqlite3.
DATABASE_USER = 'dev'             # Not used with sqlite3.
DATABASE_PASSWORD = 'testtest'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/astatic/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nbpp-859!m#ymr#j#hl6fskjl*@75jus@9jw=9s$ar+km!@r&@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    #'django.core.context_processors.debug',
    #'django.core.context_processors.i18n',
    #'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'wiki.helpers.context_processor',
)

MIDDLEWARE_CLASSES = (
    'wiki.middleware.SiteTagMiddleware', #handles subdomains
    'django.middleware.common.CommonMiddleware', #adds ending /. Doesn't work...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_fakewall.middleware.FakewallMiddleware', #maintenance mode
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Below is not needed...
    #os.path.join(SITE_ROOT, 'wiki/templates'),
)

INSTALLED_APPS = (
    'django_auth_longer_email', #increase user email length to 254
    'django.contrib.auth',
    'django.contrib.contenttypes', #required by auth
    'django.contrib.sessions',
    #'django.contrib.sites', 
    'django.contrib.humanize', #for apnumber in template
    'django.contrib.admin', #admin site
    'django.contrib.messages',
    'base',
    'wiki_admin',
    'django_rpx_plus', #Put this after our app with template over-rides.
    'wiki',
    #'test_utils', #for testmaker server
)

AUTHENTICATION_BACKENDS = (
    'django_rpx_plus.backends.RpxBackend', 
    'django.contrib.auth.backends.ModelBackend', #default django auth
    'common.backends.WikiPermBackend', #auth for wiki pages.
    'common.backends.WikiAdminPermBackend', #auth for wiki admin.
)

#Allow to work on all subdomains:
#TODO: Move this to local-settings.py
SESSION_COOKIE_DOMAIN = '.suppletext.com' #cannot have any ports on the end.
#SESSION_COOKIE_NAME = 'sessid'
#SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#Additional user data (ie. User Profile)
AUTH_PROFILE_MODULE = 'base.UserProfile'

# Here are some settings related to auth urls. django has default values for them
# as specified on page: http://docs.djangoproject.com/en/dev/ref/settings/. You
# can override them if you like.
#account.
#LOGIN_REDIRECT_URL = '/accounts/dashboard/' #default: '/accounts/profile/'
#LOGIN_URL = '' #default: '/accounts/login/'
#LOGOUT_URL = '' #default: '/accounts/logout/'

########################################
# django messages framework settings:  #
########################################

#First uses CookieStorage for all messages, falling back to using
#SessionStorage for the messages that could not fit in a single cookie.
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'

#############################
# django-fakewall settings: #
#############################

#Turns the maintenance mode fakewall on if True, off if False (default).
FAKEWALL_MODE = False

#The secret code that user enters as part of URL params to bypass the
#fakewall:
FAKEWALL_BYPASS_CODE = 'yes' #change this to something secret

########################
# reCaptcha settings:  #
########################

#Go here to generate keys: http://mailhide.recaptcha.net/apikey
MAILHIDE_PUBLIC_KEY = ''
MAILHIDE_PRIVATE_KEY = ''

###############################
# Strictly wiki settings:     #
###############################

#Middleware will set this to true if unit testing wiki. Can manually set to true
#to run testmaker for wiki.
IS_TESTING_WIKI = False

#Self-explanatory:
BASE_MEDIA_URL = '/static/base/'
WIKI_MEDIA_URL = '/static/wiki/'
#For admin:
WIKI_ADMIN_MEDIA_URL = '/static/wiki_admin/'

#Contains the current Wiki object.
#(Yes, this is a bad abuse of settings.py. But it's not messy.)
WIKI = None

#Contains the current Page object. This is very useful in creole parser macros
#to temporarily store stuff in this page object
#TODO: Make sure we are actually using this.
PAGE = None

#Reserved site tags's that cannot be used for wikis.
RESERVED_SITE_TAGS= ('home', 'help', 'admin', 'privacy', 'policy', 'help',
                     'features', 'premium', 'tos', 'blog', 'forum', 'contact',
                     'share', 'new', 'show', 'feedback', 'user', 'about',
                     'aup', 'dmca', 'account', 'wiki', 'create', 'tour',
                     'pricing', 'suppletext', 'supplelabs', 'labs', 'admin',
                     'www', 'static')

#For better readability, we excluded some characters from being in the
#short_id. This defines the characters excluded from the short_id:
EXCLUDED_SHORTID_CHARS = ('o', '0', 'l', '1')

#Defines the wiki_id that contains our global pages
GLOBAL_WIKI_ID = 1

#Header search regex. NOTE: The ending ='s are optional.
SEARCH_HEADER = re.compile('^\s*=\s*([\S ]+)')

#Classes of users that we can use to specify default read and write permissions.
PERMISSION_CHOICES = (
    ('anyone', 'Anyone'),
    ('loggedin', 'Logged in users'),
    ('contributor', 'Contributors only'),
    ('administrator', 'Administrators only'),
)

#Used in adding user admin.
USER_ROLE_CHOICES = (
    ('contributor', 'Contributors'),
    ('administrator', 'Administrators'),
)

#Number of context lines to show when diffing:
DIFF_CONTEXT_LINES = 3

############################
#django_rpx_plus settings: #
############################
RPXNOW_API_KEY = ''

# The realm is the subdomain of rpxnow.com that you signed up under. It handles 
# your HTTP callback. (eg. http://mysite.rpxnow.com implies that RPXNOW_REALM  is
# 'mysite'.
RPXNOW_REALM = 'suppletext'

# (Optional)
#RPX_TRUSTED_PROVIDERS = ''

# (Optional)
# RPX requires a token_url to be passed to its APIs. The token_url is an
# absolute url that points back to the rpx_response view. By default, this
# token_url is constructed by using request.get_host(). However, there may
# be cases where rpx_response is hosted on another domain (eg. if the website
# is using subdomains). Therefore, we can force the base url to be fixed instead
# of auto-detected. 
# Note: This is the HOSTNAME without the beginning 'http://' or trailing slash
#       part. An example hostname would be: localhost:8000
# Protip: You can set RPX_BASE_SITE_HOST in middleware too.
#RPX_BASE_SITE_HOST = '' #Set in middleware

# If it is the first time a user logs into your site through RPX, we will send 
# them to a page so that they can register on your site. The purpose is to 
# let the user choose a username (the one that RPX returns isn't always suitable)
# and confirm their email address (RPX doesn't always return the user's email).
REGISTER_URL = '/accounts/register/'


#Import any local settings (ie. production environment) that will override
#these development environment settings.
try:
    from local_settings import *
except ImportError:
    pass 
