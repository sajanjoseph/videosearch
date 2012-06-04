import os
import simplejson
import settings
from django.test import TestCase
from django.core.urlresolvers import reverse

from vsearch import models,views
from vsearch.views import create_entrylist,create_sublists,create_dict_list,parse_subtitle_file
from vsearch.views import search_for_words_in_dict_list,create_subtitle_filename
from vsearch.views import  convert_to_seconds,convert_to_seconds_tpls

from django.http import HttpResponseServerError

class SubRipParseTest(TestCase):
    def setUp(self):
        self.filename = os.path.join(settings.MEDIA_ROOT,'uploads','cs101_unit1_03_l_Programming.srt')
        
    
    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.filename))
        
    def test_create_subtitle_filename(self):
        vidname = 'myvideo.webm'
        self.assertEqual(settings.MEDIA_ROOT+'/uploads/myvideo.srt',create_subtitle_filename(vidname))
    
    def test_convert_to_seconds(self):        
        t1 = '00:00:08,000'
        t2 = '00:00:14,066'
        t3 = '00:01:42,000'
        self.assertEqual(8,convert_to_seconds(t1))
        self.assertEqual(14,convert_to_seconds(t2))
        self.assertEqual(102,convert_to_seconds(t3))
        
    def test_convert_to_seconds_tpls(self):
        input_tpls = [('This is supposed to be a toaster.', '00:00:08,000'),
                ('A toaster - well, we can do more than one thing with a toaster maybe.', '00:00:14,066'),
                ("If we're really creative we could make a bicycle from the toaster.", '00:00:51,000'),
                ('So without a program, a computer is even less useful than a toaster.', '00:00:57,000'),
                ('And the power of a computer is that, unlike a toaster,', '00:01:05,000'),
                ('into a game-playing machine, into a toaster without anywhere to put the bread,', '00:01:42,000')]
        result_tpls = convert_to_seconds_tpls(input_tpls)
        expected_tpls = [('This is supposed to be a toaster.', 8),
                         ('A toaster - well, we can do more than one thing with a toaster maybe.', 14),
                         ("If we're really creative we could make a bicycle from the toaster.", 51),
                         ('So without a program, a computer is even less useful than a toaster.', 57),
                         ('And the power of a computer is that, unlike a toaster,', 65),
                         ('into a game-playing machine, into a toaster without anywhere to put the bread,', 102)]
        
        self.assertEqual(expected_tpls,result_tpls)
    
    def test_ajax_sendname(self):
        data={'name':'myownvideo.webm'}
        response = self.client.post(reverse('sendname'),data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200,response.status_code)
        self.assertEqual('myownvideo.webm',views.videofilename)
    
    def test_ajax_search(self):
        data={'kwords':'toaster'}
        response = self.client.post(reverse('sendname'),{'name':'cs101_unit1_03_l_Programming.webm'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200,response.status_code)
        response = self.client.post(reverse('search'),data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200,response.status_code)
        #print 'resp=',response
        self.assertEqual(response['Content-Type'],'application/json')
        self.assertTrue(response.content[0]=='{')
        self.assertTrue(response.content[-1]=='}')
        d = simplejson.loads(response.content)
        self.assertEqual(d.get('8'),'This is supposed to be a toaster.')
        self.assertEqual(d.get('57'),'So without a program, a computer is even less useful than a toaster.')
       
    def test_non_ajax_search_returns_error(self):
        data={'kwords':'toaster'}
        response = self.client.post(reverse('sendname'),{'name':'cs101_unit1_03_l_Programming.webm'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response['Content-Type'],'application/json')
        self.assertEqual(200,response.status_code)
        response = self.client.post(reverse('search'),data)
        self.assertEqual(500,response.status_code)
        d = simplejson.loads(response.content)
        self.assertEqual(d.get('msg'),'No POST data sent.')


#    def test_entrylist_create(self):
#        entrylist = create_entrylist(self.filename)
#        print 'entrylist=',entrylist    
