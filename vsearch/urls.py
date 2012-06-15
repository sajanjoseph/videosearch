
from django.conf.urls.defaults import *
urlpatterns=patterns('',

url(r'^account/',include('vsearch.accturls.login')),
url(r'^search/$', 'vsearch.views.ajax_search',name='search'),
url(r'^sendname/$', 'vsearch.views.sendname',name='sendname'),
url(r'^upload/$', 'vsearch.views.ajax_store_uploaded_file',name='ajax_upload'),
url(r'^$', 'vsearch.views.index',dict(template_name = 'vsearch/index.html'), name = 'home'),
)
