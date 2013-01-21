'''
Created on Jun 10, 2012

@author: sajan
'''

from registration.urls import urlpatterns as regpatterns
from registration.forms import RegistrationFormUniqueEmail
from django.conf.urls.defaults import *

urlpatterns=patterns('',
url(r'^login/$','django.contrib.auth.views.login',{'template_name':'vsearch/mylogin.html'},name='vsearch_login'),
url(r'^logout/$', 'vsearch.views.logout', {}, name = 'vsearch_logout'),
)

from registration.views import register
custom_reg_patterns=patterns('',
     url(r'^register/', register, 
      {'form_class':RegistrationFormUniqueEmail,'backend':'registration.backends.default.DefaultBackend' },
      
      name='registration_register'),
)
urlpatterns+=custom_reg_patterns


urlpatterns += regpatterns