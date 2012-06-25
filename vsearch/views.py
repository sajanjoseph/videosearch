# Create your views here.

from models import UserFileNameMap
import settings
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.http import  HttpResponseServerError

from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.middleware.csrf import get_token
import simplejson
import re
import codecs
import cgi
import datetime
import os
import logging
from settings import LOG_LEVEL

logging.basicConfig(
    level = LOG_LEVEL,
    format = '%(asctime)s %(levelname)s %(message)s',
)

logger = logging.getLogger(__name__)

@require_POST
@never_cache
def logout(request):
    return logout_then_login(request)

def custom_render(request,context,template):
    req_context=RequestContext(request,context)
    return render_to_response(template,req_context)

@login_required   
def index(request, template_name):
    csrf_token = get_token(request)
    return custom_render(request, {'csrf_token': csrf_token },template_name)

@login_required
def store_uploaded_file(request,template_name):
    to_return = {}
    store_message="failure"
    if request.method == 'POST':
        if request.FILES.has_key('subselect'):
            file = request.FILES['subselect']
            fname = request.user.username+'_'+file.name
            with open(settings.uploadpath+'/%s' % fname, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            store_message="success"
    to_return['store_message']= store_message
    if store_message == "failure":
        return redirect('home')
    return custom_render(request, to_return,template_name)

@login_required
def ajax_store_uploaded_file(request):
    to_return = {}
    store_message="failure"
    if  (request.method == 'POST') and request.FILES.has_key('file'):
        #if request.FILES.has_key('file'):
        file = request.FILES['file']
        #prefix username to filename
        fname = request.user.username+'_'+file.name
        with open(settings.uploadpath+'/%s' % fname, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        store_message="success"
    to_return['store_message']= store_message
    serialized = simplejson.dumps(to_return)
    if store_message == "success":
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")


@login_required
def sendname(request):
    success = False
    to_return = {'msg':u'No POST data sent.' }
    if (request.is_ajax()) and (request.method == "POST"):
        post = request.POST.copy()
        if post.has_key('name'):
            name = post['name']
            fmap = UserFileNameMap.objects.get_or_create(fuser=request.user)[0]
            fmap.filename = name 
            fmap.save()
            #slugify is used since delete(name) fails if name contains spaces
            cache.delete(slugify(name))
            logger.debug('%s from cache deleted'%name)
            success = True
            to_return['msg'] = u"successfully sent name"
        else:
            to_return['msg'] = u"Requires name"
    serialized = simplejson.dumps(to_return)
    if success == True:
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")
"""
parse file and get a list
['1', '00:00:00,000 --> 00:00:02,000', "some text.",...]

"""   
def create_entrylist(infile):
    entrylist = []
    with codecs.open(infile, "r", "utf-8-sig") as f:
        logger.debug('parsing subtitle file:%s'%infile)
        for line in f:
            entrylist.append(str(line.strip()))
    return entrylist

"""
from entrylist create a list of lists as
[['1', '00:00:00,000 --> 00:00:02,000', "hello there"],[...],...]
or possibly
[['1', '00:00:00,000 --> 00:00:02,000', "hello there","howdy"],[...],...]
if the subrip file contains multiple text lines 

"""
def create_sublists(entrylist):
    mlist=[]
    l=[]
    for x in entrylist:
        if x != '\n' and x != '':
            l.append(x)
        else:
            if len(l)>0:
                mlist.append(l)
            l=[]
    #concat the third element with the fourth,fifth elements etc   
    for x in mlist:
        x[2:] = [" ".join(x[2:])]
    return mlist  

def create_dict_list(mlist):
    """
    go thru each sublist
    create a dict for each sublist
    combine third and rest into single string
    add to dicts
    add each dict to a dlist
    return dlist
    """
    dlist=[]
    
    for subl in mlist:
        d={}
        if re.match('\d+$',subl[0]):
            d['SeqNum']=int(subl[0].strip())
        else:
            raise ValueError(subl[0],' should be an integer')    
        if re.match('\d{2}:\d{2}:\d{2}',subl[1]):
            time_parts=subl[1].split('-->')
            time_parts=[t.strip() for t in time_parts]
            d['Start'] = time_parts[0]
            d['End'] = time_parts[1]
        else:
            raise ValueError(subl[1],' should be a start-end time range')
        if re.match('[\[*\]*\d*\w*]',subl[2]):
            
            content= (''.join(subl[2:])).replace('\n',' ').strip()
            d['Content'] = content
        else:
            raise ValueError(subl[2],' should be alphanumeric')
        dlist.append(d)
    
    return dlist

def parse_subtitle_file(infile):
    try:
        entrylist=create_entrylist(infile)
    except (ValueError, IndexError) as e:
        logger.error(str(e))
    else:
        mlist=create_sublists(entrylist)
        dlist=create_dict_list(mlist)
        return dlist
    

def search_for_words_in_dict_list(data_dict_list,keywords):
    result=[]
    for d in data_dict_list:
        for kw in keywords:
            for (k,v) in d.iteritems():
                if kw.lower() in str(v).lower():
                    result.append((v,d['Start']))
    return result

def create_subtitle_filename(username,videofilename):
    subfile_name=videofilename[:videofilename.rindex('.')]+'.srt'
    #append username to filename
    subfile_name = username+'_'+subfile_name
    subtitlefile_fullpathname = os.path.join(settings.uploadpath,subfile_name )
    return subtitlefile_fullpathname

@login_required
def ajax_search(request):
    success = False
    username = request.user.username
    to_return = {'msg':u'No POST data sent.' }
    if (request.is_ajax()) and(request.method == "POST"):
        post = request.POST.copy()
        if post.has_key('kwords'):
            kwords = post['kwords']
            kwords = cgi.escape(kwords, True)
            kwords = [x.strip() for x in kwords.split()]
            to_return['kw'] = kwords
            to_return['msg'] = u'retrieved kwords.'            
            videofilename = UserFileNameMap.objects.filter(fuser=request.user)[0].filename
            if videofilename:
                subtitle_filename = create_subtitle_filename(username,videofilename)
                dlist = cache.get(slugify(videofilename))
                if dlist:
                    logger.debug('got dlist from cache')
                else:
                    logger.debug('need to read file')
                    if os.path.isfile(subtitle_filename):
                        dlist = parse_subtitle_file(subtitle_filename)
                        cache.set(slugify(videofilename),dlist)
                    else:
                        logger.debug('Requires subtitle file')
                        to_return['msg'] = u'Requires subtitle file'                     
                
                if dlist:
                    res = search_for_words_in_dict_list(dlist,kwords)
                    res = convert_to_seconds_tpls(res)
                    for v,k in res:
                        to_return[k] = v
                    to_return['results'] = res
                    success = True
        else:
            to_return['msg'] = u'Requires keywords'
    serialized = simplejson.dumps(to_return)
    if success == True:
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")

def convert_to_seconds(timevalue):
    pt = datetime.datetime.strptime(timevalue,'%H:%M:%S,%f')
    return pt.second+pt.minute*60+pt.hour*3600

def convert_to_seconds_tpls(sample_tpls):
    res = [(k,convert_to_seconds(v)) for k,v in sample_tpls]
    return res

"""
no-ajax version
"""
@login_required
def search(request, template_name):
    user_kwords=request.GET.get('keywords')
    kwords = [x.strip() for x in user_kwords.split()]
    videofilename = UserFileNameMap.objects.filter(fuser=request.user)[0].filename
    if videofilename:
        subtitle_filename = create_subtitle_filename(videofilename)
        dlist = parse_subtitle_file(subtitle_filename)
        res = search_for_words_in_dict_list(dlist,kwords)
    kwords =[str(x) for x in kwords]
    return custom_render(request, {'keywords':kwords,'results':res },template_name)
