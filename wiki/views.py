from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.forms import widgets #used in changing field to hidden
import django.contrib.messages as messages

from wiki.forms import EditForm, PagePermissionsForm
from wiki.models import Page
from wiki.helpers import short_to_int, unified_diff
from wiki.decorators import wiki_permission_required

#from creoleparser import text2html
from wiki.utils.wikiparser import text2html
import wiki.utils.wikiparser_macros
from wiki.utils.diff_match_patch import diff_match_patch

import re #searching for first header
#from pprint import pprint
import datetime #used in edit

def home(request):
    return HttpResponseRedirect(reverse('show', args=[settings.WIKI.front_page]))

@wiki_permission_required('view')
def show(request, page_tag, rev = None):
    #Check if exist:
    try:
        #if we have a rev specified, then get only that revision
        if rev != None:
            rev = short_to_int(rev)
            p = Page.objects.get(wiki = settings.WIKI, tag = page_tag, id = rev)
        else:
            #Select the most recent version
            p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
    except Page.DoesNotExist:
        #This means that the rev specified does not exist. So we'll just
        #redirect to the most recent version.
        #TODO: Show error message with redirect.
        return HttpResponseRedirect(reverse('show', args=[page_tag]))
    except IndexError:
        #Check to see if this is one of our global pages (wiki_id is one)
        try:
            p = Page.objects.filter(wiki = settings.GLOBAL_WIKI_ID, 
                                    tag = page_tag) \
                            .order_by('-id')[0]
            #We don't want to display the "3 days ago" date on show.html
            p.created = None
        except IndexError:
            #Then redirect to edit
            #TODO: Show page doesn't exist, do you want to create?
            return HttpResponseRedirect(reverse('edit', args=[page_tag]))
    
    #TODO: Cache the output of this.
    content_html = text2html(p.content, environ = {
                                'settings': settings,
                                'wiki.page': p,
                                'wiki.macros': wiki.utils.wikiparser_macros.macros,
                                'wiki.parser': text2html,
                            })

    #Check if a page title has been set (with a macro). If not, then we check to see
    #if there is a first header that we can use as the title.
    if not hasattr(p, 'title'):
        #If there is no first header, then we set the page_title to be the page_tag:
        if not settings.SEARCH_HEADER.match(p.content):
            p.title = p.tag
    
    return render_to_response('wiki/show.html', {
                                'page': p,
                                'content_html': content_html,
                                'rev': rev, #to check if old revision used
                              }, 
                              context_instance = RequestContext(request))

@wiki_permission_required('edit')
def revert(request, page_tag, rev):
    #Get revision information
    rev_int = short_to_int(rev)
    r = Page.objects.get(wiki = settings.WIKI, tag = page_tag, id = rev_int)

    #We also get the last current page information (for saving permissions).
    #We know for SURE that at least one page exists for revert to happen so this
    #query must return at least one page.
    latest = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]

    #Now resave as current page.
    p = Page()
    p.wiki = r.wiki
    p.tag = r.tag
    p.content = r.content
    p.note = 'Reverted to revision '+str(rev)+'.'
    p.author = r.author
    p.ip_address = r.ip_address
    
    #We keep same permissions as the previous page.
    p.can_view = latest.can_view
    p.can_edit = latest.can_edit
    p.can_special = latest.can_special

    p.save()

    messages.success(request, 'You have successfully reverted to revision '+str(rev)+'.')
    return HttpResponseRedirect(reverse('show', args=[page_tag]))

@wiki_permission_required('edit')
def edit(request, page_tag, rev = None):
    if request.method == 'POST':
        form = EditForm(request.POST)
        #Also check to see if we are 're-editing' the page:
        if form.is_valid() and request.POST.get('action') != 'Edit':
            data = form.cleaned_data
            #print data

            #Check for preview or save. In both cases, we'll create a new page
            #(since we always want to save a new record.
            p = Page()
            p.wiki = settings.WIKI 
            p.tag = page_tag
            p.content = data['content']
            p.note = data['note']
            #If user is anonymous, then leave the p.author field blank.
            if request.user.is_authenticated() and request.user.is_active:
                p.author = request.user
            p.ip_address = request.META['REMOTE_ADDR']
            if request.POST.get('action') == 'Save' or request.POST.get('action') == 'Force Save':
                #TODO: Check if there has been a change in content. If no change, then
                #don't save.

                #We also save the previous (most current) page permission.
                try:
                    latest = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
                    p.can_view = latest.can_view
                    p.can_edit = latest.can_edit
                    p.can_special = latest.can_special

                    #We also check for edit conflict. That is, if the previous edit
                    #creation datetime is >= the current edit datetime. We only check
                    #for conflict when the action is "Save" and NOT "Force Save".
                    if latest.created >= data['time'] and latest.content != p.content:
                        #We also need to check if the 'latest' timestamp sent by
                        #the form is >= the current 'latest' timestamp at the time
                        #of this submission. If so, that means someone edited the
                        #article while we were resolving conflicts. In that case,
                        #show the conflicts again.
                        if request.POST.get('action') == 'Save' or data['latest_time'] < latest.created:
                            #Display conflict diff
                            diffs = unified_diff(latest.content, p.content)

                            return render_to_response('wiki/conflict.html', {
                                                        'page_tag': page_tag,
                                                        'page': p, #Can be None
                                                        'form': form,
                                                        'rev': rev, #Used to check if using rev
                                                        'latest': latest,
                                                        'diffs': diffs,
                                                      }, 
                                                      context_instance = RequestContext(request))

                except IndexError:
                    #Means that this page doesn't exist yet. That's fine. Global
                    #perm will be used for the page.
                    pass

                p.save()

                #Return to show page
                return HttpResponseRedirect(reverse('show', args=[page_tag]))
            else: #Anything else will be considered 'Preview'
                content_html = text2html(p.content, environ = {
                                            'settings': settings,
                                            'wiki.page': p,
                                            'wiki.macros': wiki.utils.wikiparser_macros.macros,
                                            'wiki.parser': text2html,
                                        })

                #Check if a page title has been set (with a macro). If not, then we check to see
                #if there is a first header that we can use as the title.
                if not hasattr(p, 'title'):
                    #If there is no first header, then we set the page_title to be the page_tag:
                    if not settings.SEARCH_HEADER.match(p.content):
                        p.title = p.tag

                #Change the content field to hidden
                form.fields['content'].widget = widgets.HiddenInput()
                return render_to_response('wiki/preview.html', {
                                            'page_tag': page_tag,
                                            'page': p, #Can be None
                                            'content_html': content_html,
                                            'form': form,
                                            #'from' allows us to determine if we will
                                            #do specific stuff for conflict case.
                                            'from': request.GET.get('from'),
                                          }, 
                                          context_instance = RequestContext(request))
        else:
            #We are re-editing the page from preview or form was invalid.
            #Either way, we only have data from the form submission and so we
            #display that.
            p = None
    else: 
        #Otherwise, form was not submitted. We prepopulate the form:
        try:
            #If we have a rev specified, then get only that revision
            if rev != None:
                rev = short_to_int(rev)
                p = Page.objects.get(wiki = settings.WIKI, tag = page_tag, id = rev)
            else:
                #Select the most recent version
                p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
            #Since our EditForm is a ModelForm, we can set it up with
            #instance.
            form = EditForm(initial = {
                'content': p.content, 
                'note': '',
                #Get rid of microseconds for time since forms.DateTimeField doesn't
                #parse microseconds. Well, it does in python 2.6 using: 
                #%Y-%m-%d %H:%M:%S.%f as input_formats.
                'time': str(datetime.datetime.now()).split('.')[0],
            })
        except Page.DoesNotExist:
            #This means that the rev specified does not exist. So we'll just
            #redirect to the most recent version.
            #TODO: Show error message with redirect.
            return HttpResponseRedirect(reverse('edit', args=[page_tag]))
        except IndexError:
            #Check to see if this is one of our global pages
            try:
                p = Page.objects.filter(wiki = settings.GLOBAL_WIKI_ID, 
                                        tag = page_tag) \
                                .order_by('-id')[0]
                form = EditForm(initial = {
                    'content': p.content, 
                    'note': '',
                    'time': str(datetime.datetime.now()).split('.')[0],
                })
            except IndexError:
                #Okay, we don't have a global page. Display a blank form.
                form = EditForm(initial = {
                    'time': str(datetime.datetime.now()).split('.')[0],
                })
                p = None

    #Set up and prepopulate the form for page permissions (if page exists).
    if p == None: #Either this is a new page, or we got here from preview.
        #See if we can grab existing page.
        try:
            p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
        except IndexError:
            #Do nothing, this is a new page.
            pass

    page_permissions_form = None
    if request.user.has_perm('page.can_special', p):
        try:
            page_permissions_form = PagePermissionsForm(initial = {
                                        'view': p.can_view,
                                        'edit': p.can_edit,
                                        })
        except AttributeError:
            #Means that this page totally doesn't exist at all so we can't access
            #p.can_view and p.can_edit.
            pass

    return render_to_response('wiki/edit.html', {
                                'page_tag': page_tag,
                                'page': p, #Can be None
                                'form': form,
                                'page_permissions_form': page_permissions_form,
                                'rev': rev, #Used to check if using rev
                              }, 
                              context_instance = RequestContext(request))

@wiki_permission_required('view')
def history(request, page_tag):
    p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')
    
    #Check if exist:
    if len(p) <= 0:
        return HttpResponseRedirect(reverse('show', args=[page_tag]))

    
    return render_to_response('wiki/history.html', {
                                'page': p[0],
                                'history': p,
                              }, 
                              context_instance = RequestContext(request))

@wiki_permission_required('view')
def compare(request, page_tag, a = None, b = None):
    #Check if a and b are set using GET
    if a == None and b == None:
        if request.method == 'GET' and len(request.GET.getlist('rev')) == 2:
            a = request.GET.getlist('rev')[0]
            b = request.GET.getlist('rev')[1]
        else:
            return HttpResponseRedirect(reverse('history', args=[page_tag]))
    #a and b are short ids, so convert to int
    a = short_to_int(a)
    b = short_to_int(b)

    #Always have the smaller number first
    if b < a:
        temp = a
        a = b
        b = temp

    #Make sure both revisions exist:
    try:
        rev_a = Page.objects.get(wiki = settings.WIKI, tag = page_tag, id = a)
        rev_b = Page.objects.get(wiki = settings.WIKI, tag = page_tag, id = b)
    except Page.DoesNotExist:
        return HttpResponseRedirect(reverse('history', args=[page_tag]))
    
    diffs = unified_diff(rev_a.content, rev_b.content)

    return render_to_response('wiki/compare.html', {
                                'page': rev_a,
                                'page_b': rev_b, #used in revision number
                                'diffs': diffs,
                              }, 
                              context_instance = RequestContext(request))

@wiki_permission_required('special')
def change_page_permissions(request, page_tag):
    if request.method == 'POST': 
        form = PagePermissionsForm(request.POST)
        
        #Also check to see if we are 're-editing' the page:
        if form.is_valid():
            data = form.cleaned_data
            #print data
            
            #Make sure page exists...
            try:
                p = Page.objects.filter(wiki = settings.WIKI, tag = page_tag).order_by('-id')[0]
            except IndexError:
                raise Http404()

            #Update database. We'll check each field manually to be safe.
            role_choices = [i[0] for i in form._permission_choices]
            if data['view'] in role_choices:
                if data['view'] == 'default':
                    p.can_view = ''
                else:
                    p.can_view = data['view']
            elif data['edit'] in role_choices:
                if data['edit'] == 'default':
                    p.can_edit = ''
                else:
                    p.can_edit = data['edit']
            else:
                #Means user did not submit data that led to a valid role change.
                raise Http404()
            
            p.save()
            return HttpResponse('success')
    
    #TODO: Do not 404, but redirect.
    raise Http404()
