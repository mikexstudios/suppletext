#bldr and Markup are similar in that they are used to return macro values. But
#bldr.tag() always gets wrapped in a <p> while Markup() does not.
import genshi.builder as bldr
from genshi.core import Markup

from genshi.filters import HTMLSanitizer
#Need to wrap HTML in HTML() before passing to sanitizer.
from genshi.input import HTML, ParseError 
#Not sure how good Genshi's sanitizer is... also includes a sanitize_css()
sanitizer = HTMLSanitizer()


from wiki.models import Page
#from wiki.utils.clean_html import clean_html #requires html5lib

import cgi #for escape

#A dictionary mapping macro short names (ie. 'date') to the macro function
#(ie. created_date(...)). 
#NOTE: We cannot use underscores as part of the short name.
macros = {}

def title(macro, environ, *pos, **kw):
    '''
    Sets the title of the wiki page. Used as a block element. Does not return
    anything.
    '''
    #We want to make sure that there are no arguments and only a body. The
    #title can be a block.
    if macro.arg_string or not macro.body:
        return None

    #Set the title of the page object
    p = environ['wiki.page']
    p.title = cgi.escape(macro.body)

    return Markup('') #return nothing and do not apply <p> tags
#Register title in the macros dict.
macros['title'] = title

def created_date(macro, environ, *pos, **kw):
    '''
    Return the creation date of the page.
    Currently, not formatted.

    Should not have a body. Should not be a block. May have an arg string (for
    formatting date, which is a TODO).
    '''
    if macro.body or macro.isblock:
        return None

    p = environ['wiki.page']
    
    return bldr.tag(p.created)
#Register title in the macros dict.
macros['created-date'] = created_date

def include(macro, environ, page_tag = None, *pos, **kw):
    '''
    Return the parsed content of the page identified by arg_string.
    TODO: Allow inclusion of revision.
    '''
    #NOTE: Once page_tag is set, both pos and kw will be 0 len.
    if page_tag is None or len(pos) != 0 or len(kw) != 0:
        return None
    
    #Check for infinite recursion. We handle this by passing in the envrion, a
    #variable that keeps track of the parent pages. If this page is trying to 
    #include *any* of the parent pages, then we will kill the include.
    #First, make sure not including ourself:
    if page_tag == environ['wiki.page'].tag:
        return bldr.tag.p('Include failed: Cannot include self.', class_ = 'macro_error')
    #Next, make sure the page we are including is not contained in the
    #parent_pages set.
    if page_tag in environ.get('wiki.parent_pages', set()):
        return bldr.tag.p('Include failed: Infinite recursion.', class_ = 'macro_error')

    #Check if the page we are trying to include exists
    settings = environ['settings']
    try:
        p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
    except IndexError:
        return bldr.tag.p('Include failed: Page not found.', class_ = 'macro_error')
    
    #Make a copy of environ to send to included pages so that they can't
    #modify the environ for this page.
    environ = environ.copy()
    #Set the new page into environ
    environ['wiki.page'] = p

    #Add this page_tag to our parent_pages set (to prevent infinite
    #recursion):
    environ['wiki.parent_pages'] = environ.get('wiki.parent_pages', set()) \
                                          .union([page_tag])

    #Parse and return the page. Note that we should set the var that keeps track of
    #recursion here.
    return environ['wiki.parser'].generate(p.content, environ = environ)
#Register title in the macros dict.
macros['include'] = include


#def transclude(macro,environ,pagename=None,*pos,**kw):
#    '''
#    Works like ``include`` except that ``environ[metadata_page]`` is set to
#    the calling page.
#    '''

def include_raw(macro, environ, page_tag = None, *pos, **kw):
    '''
    Return the parsed content of the page identified by arg_string.
    TODO: Allow inclusion of revision.
    '''
    #NOTE: Once page_tag is set, both pos and kw will be 0 len.
    if page_tag is None or len(pos) != 0 or len(kw) != 0:
        return None
    
    #Check if the page we are trying to include exists
    settings = environ['settings']
    try:
        p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
    except IndexError:
        return bldr.tag.p('Include failed: Page not found.', class_ = 'macro_error')
    
    return bldr.tag.pre(p.content, class_ = 'wikitext')
#Register title in the macros dict.
macros['include-raw'] = include_raw

#def include_source(macro,environ,pagename=None,*pos,**kw):
#    '''
#    Return the parsed text of the page identified by arg_string, rendered
#    in a <pre> block.
#    '''

#def source(macro,environ,*pos,**kw):
#    """Return the parsed text of body, rendered in a <pre> block."""


#def pre(macro,environ,*pos,**kw):
#    """Return the raw text of body, rendered in a <pre> block."""


#def float_div(macro,environ,side='right',style='', *pos,**kw):
#    '''
#    Return the parsed text of body, rendered in a <div> block. The div element
#    gets a a style attribute to float the content right or left, based on the
#    arg_string.
#    '''


def div(macro, environ, class_ = None, id = None, style = None, *pos, **kw):
    '''
    Return the parsed text of body, rendered in a <div> block. Three attributes
    can be set on the div: class, id, and style.

    Can be used as both a block and inline element.
    '''
    #First, make sure our arguments are correct. If they are, pos and kw will
    #always have zero length.
    if len(pos) != 0 or len(kw) != 0:
        return None

    #Next, we want to make sure that there is a body. 
    if not macro.body:
        return None

    #Sanitize styles
    #TODO: Think whether we need styles or not. This poses a security risk.
    if style:
        style = ';'.join(sanitizer.sanitize_css(style))

    #Passing block (or inline) context to parser helps it determine what tags will
    #be used to wrap the output.
    if macro.isblock:
        context = 'block' #will add <p> wrapping the output.
    else:
        context = 'inline' #no <p> will be added.
    contents = environ['wiki.parser'].generate(macro.body, environ = environ, 
                                               context = context)
    
    #You might wonder why we can't just do something like:
    #Markup('<div ...>') + content + Markup('</div>')
    #and have the content be parsed by the wiki parser automatically.
    #Well, tried that, and it doesn't work. Once a Markup() or bldr object is
    #introduced, no further parsing on the string is performed.
    return bldr.tag.div(contents, id = id, class_ = class_, style = style)
macros['div'] = div

def span(macro, environ, class_ = None, id = None, style = None, *pos, **kw):
    """
    Return the parsed text of body, rendered in a <span> block. Three attributes
    can be set on the span: class, id, and style.

    Can be used as both a block (not recommended) and inline element.
    """
    #First, make sure our arguments are correct. If they are, pos and kw will
    #always have zero length.
    if len(pos) != 0 or len(kw) != 0:
        return None

    #Next, we want to make sure that there is a body. 
    if not macro.body:
        return None

    #Technically, should not be used as a block wikitext macro element, but we'll
    #let that slide.

    #Sanitize styles
    #TODO: Think whether we need styles or not. This poses a security risk.
    if style:
        style = ';'.join(sanitizer.sanitize_css(style))

    #Since we have a span (inline element), we pass 'inline' context to the
    #parser so that <p> won't wrap output.
    contents = environ['wiki.parser'].generate(macro.body, environ = environ, 
                                               context = 'inline')
    
    return bldr.tag.span(contents, id = id, class_ = class_, style = style)
macros['span'] = span

def html(macro, environ, *pos, **kw):
    '''
    Returns macro.body through an HTML sanitizer.

    Can be used as both a block and inline element.
    '''
    #We want to make sure that there are no arguments and only a body. 
    if macro.arg_string or not macro.body:
        return None

    #Sanitize HTML. html5lib's sanitizer is more secure, but also buggier. So
    #we're going to stick with genshi.
    sanitizer = HTMLSanitizer(safe_attrs=HTMLSanitizer.SAFE_ATTRS | set(['style']))
    try:
        sanitized_html = HTML(macro.body) | sanitizer
    except ParseError:
        return bldr.tag.p('There was an error in parsing the provided HTML. Please make sure that it is valid.', 
                          class_ = 'error')

    return Markup(sanitized_html)
macros['html'] = html

def comment(macro, environ, *pos, **kw):
    '''
    Does not return anything. Use for comments.
    '''
    #We want to make sure that there are no arguments and only a body. Can be
    #a block.
    if macro.arg_string or not macro.body:
        return None

    return Markup('') #return nothing and do not apply <p> tags
#Register title in the macros dict.
macros['comment'] = comment
