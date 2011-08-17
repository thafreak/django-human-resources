from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models import CMSPlugin

from human_resources.models import JobOpportunity

class JobOpportunityPlugin(CMSPluginBase):
	module = _('Human Resources')
	model = CMSPlugin
	name = _('Published Jobs')
	render_template = 'human_resources/cms/published_jobs.html'
	#text_enabled = True
	admin_preview = False
	
	def render(self, context, instance, placeholder):
		request = context["request"]
		
		jobs = JobOpportunity.objects.filter(published_status=2)
		
		context.update({
			"jobs": jobs,
		})
		
		return context
	

plugin_pool.register_plugin(JobOpportunityPlugin)