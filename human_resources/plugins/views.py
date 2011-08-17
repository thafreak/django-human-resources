from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import get_object_or_404

from human_resources.models import JobOpportunity

def job_opportunity(request, slug):
	job = get_object_or_404(
		JobOpportunity,
		slug=slug,
		published_status=JobOpportunity.OPPORTUNITY_STATUS_CHOICES[1][0]
	)
	
	other_jobs = JobOpportunity.objects.filter(published_status=JobOpportunity.OPPORTUNITY_STATUS_CHOICES[1][0]).exclude(slug=slug)
	context = {
		"job": job,
		"other_jobs": other_jobs,
	}
	return render_to_response(
		"human_resources/job_page.html",
		context,
		context_instance=RequestContext(request)
	)