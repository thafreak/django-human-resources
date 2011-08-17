from django.conf.urls.defaults import *

urlpatterns = patterns('human_resources.plugins.views',
	url(r'^(?P<slug>[-\w]+)/', 'job_opportunity', name="job_page"),	
)