# Create your views here.
from models import UploadFileForm
import settings
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseBadRequest
from django.http import  HttpResponseServerError,Http404
from settings import MEDIA_ROOT

from django.middleware.csrf import get_token
import simplejson
import re
import codecs
import cgi
import datetime
import os


videofilename=''

def custom_render(request,context,template):
    req_context=RequestContext(request,context)
    return render_to_response(template,req_context)
    
def index(request, template_name):
    csrf_token = get_token(request)
    return custom_render(request, {'csrf_token': csrf_token },template_name)

def store_uploaded_file(request,template_name):
    to_return = {}
    store_message="failure"
    if request.method == 'POST':
        if request.FILES.has_key('subselect'):
            file = request.FILES['subselect']
            with open(settings.uploadpath+'/%s' % file.name, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            store_message="success"
    to_return['store_message']= store_message
    if store_message == "failure":
        return redirect('home')
    return custom_render(request, to_return,template_name)

def ajax_store_uploaded_file(request):
    to_return = {}
    store_message="failure"
    if  (request.method == 'POST'):
        if request.FILES.has_key('file'):
            file = request.FILES['file']
            with open(settings.uploadpath+'/%s' % file.name, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            store_message="success"
    to_return['store_message']= store_message
    to_return['store_message']= store_message
    serialized = simplejson.dumps(to_return)
    if store_message == "success":
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")


def sendname(request):
    success = False
    to_return = {'msg':u'No POST data sent.' }
    if (request.is_ajax()) and (request.method == "POST"):
        post = request.POST.copy()
        if post.has_key('name'):
            name = post['name']
            global videofilename
            videofilename = name
            success = True
        else:
            to_return['msg'] = u"Requires name"
    serialized = simplejson.dumps(to_return)
    if success == True:
        return HttpResponse(serialized, mimetype="application/json")
    else:
        return HttpResponseServerError(serialized, mimetype="application/json")
   
def create_entrylist(infile):
    r=[]
    with codecs.open(infile, "r", "utf-8-sig") as f:
        for line in f:
            r.append(str(line.strip()))
    return r

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
    return mlist  

"""
go thru each sublist
create a dict for each sublist
combine third and rest into single string
add to dicts
add each dict to a dlist
return dlist
"""
def create_dict_list(mlist):
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
    entrylist=create_entrylist(infile)
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

def create_subtitle_filename(videofilename):
    subfile_name=videofilename[:videofilename.rindex('.')]+'.srt'
    #return os.path.join(MEDIA_ROOT,'uploads',subfile_name)
    return os.path.join(settings.uploadpath,subfile_name )

def ajax_search(request):
    success = False
    to_return = {'msg':u'No POST data sent.' }
    if (request.is_ajax()) and(request.method == "POST"):
        post = request.POST.copy()
        if post.has_key('kwords'):
            kwords = post['kwords']
            kwords = cgi.escape(kwords, True)
            kwords = [x.strip() for x in kwords.split()]
            to_return['kw'] = kwords
            to_return['msg'] = u'retrieved kwords.'
            if videofilename:
                subtitle_filename = create_subtitle_filename(videofilename)
                if os.path.isfile(subtitle_filename):
                    dlist = parse_subtitle_file(subtitle_filename)
                    res = search_for_words_in_dict_list(dlist,kwords)
                    res = convert_to_seconds_tpls(res)
                    for v,k in res:
                        to_return[k] = v
                    to_return['results'] = res
                    success = True
                else:
                    to_return['msg'] = u'Requires subtitle file'
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

def search(request, template_name):
    success=False
    user_kwords=request.GET.get('keywords')
    kwords = [x.strip() for x in user_kwords.split()]
    subtitle_file = None
    if videofilename:
        subtitle_filename = create_subtitle_filename(videofilename)
        dlist = parse_subtitle_file(subtitle_filename)
        res = search_for_words_in_dict_list(dlist,kwords)
        success = True
    kwords =[str(x) for x in kwords]
    return custom_render(request, {'keywords':kwords,'results':res },template_name)
