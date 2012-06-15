'''
Created on Jun 10, 2012

@author: sajan
'''

from registration.urls import urlpatterns as regpatterns
from django.conf.urls.defaults import *

urlpatterns=patterns('',
url(r'^login/$','django.contrib.auth.views.login',{'template_name':'vsearch/mylogin.html'},name='vsearch_login'),
url(r'^logout/$', 'vsearch.views.logout', {}, name = 'vsearch_logout'),
)
urlpatterns += regpatterns