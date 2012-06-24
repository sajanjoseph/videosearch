import os
import simplejson
import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from vsearch import models,views
from vsearch.views import create_entrylist,create_sublists,create_dict_list,parse_subtitle_file
from vsearch.views import search_for_words_in_dict_list,create_subtitle_filename
from vsearch.views import  convert_to_seconds,convert_to_seconds_tpls

class SubRipParseTest(TestCase):
    def setUp(self):
        super(SubRipParseTest,self).setUp()
        self.client.login(username='sajan',password='sajan')
        self.filename = os.path.join(settings.testpath,'smallfile.srt')
        self.mult_textlines_file = os.path.join(settings.testpath,'mult_textlines.srt')
        self.invalidfile = os.path.join(settings.testpath,'invalid_file.srt')
        self.no_seq_num = os.path.join(settings.testpath,'no_seq_num.srt')
        self.no_time_range = os.path.join(settings.testpath,'no_time_range.srt')
        base_name = 'cs101_unit1_03_l_Programming.srt'
        self.srcfile = os.path.join(settings.testpath,base_name)
        self.destfile = os.path.join(settings.uploadpath,'sajan_'+base_name)
        
    def tearDown(self):
        #remove uploadedfile if exists
        if os.path.isfile(self.destfile):
            os.remove(self.destfile)

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.filename))

    def test_create_subtitle_filename(self):
        username = 'sajan'
        vidname = 'myvideo.webm'
        self.assertEqual(os.path.join(settings.uploadpath,'sajan_myvideo.srt'),create_subtitle_filename(username,vidname))

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

    def test_create_entrylist(self):
        expected = ['1','00:00:00,000 --> 00:00:02,000', "[D. Evans] Let's get started with programming.",'',
                    '2', '00:00:02,000 --> 00:00:05,000','Programming is really the core of computer science.','',
                    '3','00:00:05,000 --> 00:00:08,000','Most machines are designed to do just one thing.','']
        e_list = create_entrylist(self.filename)
        self.assertEquals(expected,e_list)

    def test_create_entrylist_mult_textlines(self):
        elist = create_entrylist(self.mult_textlines_file)
        expected = ['1', '00:00:00,000 --> 00:00:02,000', "[D. Evans] Let's get started with programming.", '',
                    '2', '00:00:02,000 --> 00:00:05,000', 'Programming is really the core of computer science.',
                       'Programmers are not aliens', 'even though they have strange habits,',
                       'like mumbling to themselves while working.', '',
                    '3', '00:00:05,000 --> 00:00:08,000', 'Most machines are designed to do just one thing.', '']
        self.assertEquals(expected,elist)

    
    def test_create_sublists(self):
        entry_list = ['1','00:00:00,000 --> 00:00:02,000', "[D. Evans] Let's get started with programming.",'',
                  '2', '00:00:02,000 --> 00:00:05,000','Programming is really the core of computer science.','',
                  '3','00:00:05,000 --> 00:00:08,000','Most machines are designed to do just one thing.','']
        
        expected =[['1', '00:00:00,000 --> 00:00:02,000', "[D. Evans] Let's get started with programming."],
                   ['2', '00:00:02,000 --> 00:00:05,000','Programming is really the core of computer science.'],
                   ['3','00:00:05,000 --> 00:00:08,000','Most machines are designed to do just one thing.']
                  ]
        sub_lists = create_sublists(entry_list)
        self.assertEquals(expected,sub_lists)
        
    def test_create_sublists__mult_textlines(self):
        input = ['1', '00:00:00,000 --> 00:00:02,000', "[D. Evans] Let's get started with programming.", '',
                    '2', '00:00:02,000 --> 00:00:05,000', 'Programming is really the core of computer science.',
                       'Programmers are not aliens', 'even though they have strange habits,',
                       'like mumbling to themselves while working.', '',
                    '3', '00:00:05,000 --> 00:00:08,000', 'Most machines are designed to do just one thing.', '']
        sub_lists = create_sublists(input)
        expected = [
                    ['1', '00:00:00,000 --> 00:00:02,000', "[D. Evans] Let's get started with programming."],
                    ['2', '00:00:02,000 --> 00:00:05,000', 'Programming is really the core of computer science. Programmers are not aliens even though they have strange habits, like mumbling to themselves while working.'],
                    ['3', '00:00:05,000 --> 00:00:08,000', 'Most machines are designed to do just one thing.']
                   ]
        self.assertEquals(expected,sub_lists)
    
    def test_create_dict_list(self):
        sublist = [['1', '00:00:00,000 --> 00:00:02,000', "[D. Evans] Let's get started with programming."],
                   ['2', '00:00:02,000 --> 00:00:05,000','Programming is really the core of computer science.'],
                   ['3','00:00:05,000 --> 00:00:08,000','Most machines are designed to do just one thing.']
                  ]
        expected=[{'SeqNum':1,'Start':'00:00:00,000','End':'00:00:02,000','Content':"[D. Evans] Let's get started with programming."},
                  {'SeqNum':2,'Start':'00:00:02,000','End':'00:00:05,000','Content':'Programming is really the core of computer science.'},
                  {'SeqNum':3,'Start':'00:00:05,000','End':'00:00:08,000','Content':'Most machines are designed to do just one thing.'}]
        dlist = create_dict_list(sublist)
        self.assertEquals(expected,dlist)

    def test_invalid_subripfile(self):
        self.assertRaises(IndexError,parse_subtitle_file,self.invalidfile)
        
    def test_subripfile_with_missing_sequence_number(self):
        self.assertRaises(ValueError,parse_subtitle_file,self.no_seq_num)
        
    def test_subripfile_with_missing_time_range(self):
        self.assertRaises(ValueError,parse_subtitle_file,self.no_time_range)
        

    def test_ajax_sendname(self):
        data={'name':'myownvideo.webm'}
        response = self.client.post(reverse('sendname'),data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200,response.status_code)
        fuser = User.objects.get(username='sajan')
        videofilename = models.UserFileNameMap.objects.filter(fuser=fuser)[0].filename
        self.assertEqual('myownvideo.webm',videofilename)
        
    def test_ajax_sendname_missing_data(self):
        data={}
        response = self.client.post(reverse('sendname'),data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(500,response.status_code)
        self.assertEquals(response['Content-Type'],'application/json')
        d = simplejson.loads(response.content)
        self.assertEquals(d['msg'],'Requires name')
        
    def test_upload_file(self):
        self.assertTrue(os.path.isfile(self.srcfile))
        self.assertFalse(os.path.isfile(self.destfile))
        with open(self.srcfile) as fp:
            response = self.client.post(reverse('ajax_upload'),{'file':fp}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200,response.status_code)
        self.assertTrue(os.path.isfile(self.destfile))

#    def test_ajax_search(self):
#        data={'kwords':'toaster'}
#        response = self.client.post(reverse('sendname'),{'name':'cs101_unit1_03_l_Programming.webm'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#        self.assertEqual(200,response.status_code)
#        response = self.client.post(reverse('search'),data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#        self.assertEqual(200,response.status_code)
#        self.assertEqual(response['Content-Type'],'application/json')
#        self.assertTrue(response.content[0]=='{')
#        self.assertTrue(response.content[-1]=='}')
#        d = simplejson.loads(response.content)
#        self.assertEqual(d.get('8'),'This is supposed to be a toaster.')
#        self.assertEqual(d.get('57'),'So without a program, a computer is even less useful than a toaster.')
#       
#    def test_non_ajax_search_returns_error(self):
#        data={'kwords':'toaster'}
#        response = self.client.post(reverse('sendname'),{'name':'cs101_unit1_03_l_Programming.webm'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#        self.assertEqual(response['Content-Type'],'application/json')
#        self.assertEqual(200,response.status_code)
#        response = self.client.post(reverse('search'),data)
#        self.assertEqual(500,response.status_code)
#        d = simplejson.loads(response.content)
#        self.assertEqual(d.get('msg'),'No POST data sent.')
