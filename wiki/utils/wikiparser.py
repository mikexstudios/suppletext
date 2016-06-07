from creoleparser import core, dialects, parse_args
from django.conf import settings
from django.core.urlresolvers import reverse

#import urllib #for page_name quoting

#from model import Page

#def class_func(page_name):
#    if Page.get_by_key_name('-'+page_name) is None:
#        return 'nonexistent'

class Macro:
    def __init__(self, name, arg_string, body, isblock):
        self.name = name
        self.arg_string = arg_string
        self.body = body
        self.isblock = isblock

def macro_func(name,arg_string,body,isblock,environ):
    
    if name in environ['wiki.macros']:
        macro = Macro(name, arg_string, body, isblock)
        pos, kw = parse_args(arg_string)
        try:
            value = environ['wiki.macros'][name](macro, environ, *pos,**kw)
        except TypeError:
            value = None
        return value
    else:
        return None

def path_func(page_name):
    '''
    Setting wiki_links_base_url doesn't work since that only gets parsed once.
    So we essentially use this as a wrapper around reverse().
    '''
    #page_name = urllib.quote_plus(page_name)
    #TODO: Disallow certain characters here?
    #TODO: Catch exception here
    return reverse('show', args=[page_name])
   
dialect = dialects.create_dialect(
    dialects.creole11_base,
    #no_wiki_monospace=False,
    #wiki_links_class_func=class_func,
    blog_style_endings = True,
    wiki_links_path_func = path_func,
    macro_func=macro_func)

text2html = core.Parser(dialect)

