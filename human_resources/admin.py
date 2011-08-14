from itertools import chain

from django.contrib import admin
from django.db.models import URLField
from django.http import HttpResponseRedirect

from human_resources.models import Person, WebLink, JobOpportunity, \
NiceToHave, Candidacy, Position, Qualification, Responsibility, \
ContractType, Evaluation, Interview, File, Benefit
from human_resources.forms import EvaluationAddForm, EvaluationChangeForm
from human_resources.widgets import WebLinkWidget




class HRAdmin(admin.ModelAdmin):
	readonly_fields = ('date_added', 'date_modified')


class HRTabularInline(admin.TabularInline):
	pass


class WebLinkInline(HRTabularInline):
	model = WebLink
	extra = 0
	
	formfield_overrides = {
		URLField: {'widget': WebLinkWidget},
	}


class FileInline(HRTabularInline):
	model = File
	extra = 0

class PersonAdmin(HRAdmin):
	
	def name(self, item):
		return u'%s, %s' %(item.last_name, item.first_name)
	name.admin_order_field = 'last_name'
	
	def person_files(self, item):
		html = ""
		if item.files.exists():
			for f in item.files.all():
				html = html + '<li><a target="_blank" href="' + f.person_file.url + '">' + f.name + '</a></li>'
			html = "<ul>" + html + "</ul>"
		return html
	person_files.allow_tags = True
		
	
	def contact_info(self, item):
		html = ""
		if item.email or item.mobile_phone or item.other_phone:
			if item.email:
				html = html + '<li><span style="font-weight:bold;">Email: </span><a href="mailto:' + item.email + '">' + item.email + '</a></li>'
			if item.mobile_phone:
				html = html + '<li><span style="font-weight:bold;">Mobile Phone: </span>' + item.mobile_phone + '</li>'
			if item.other_phone:
				html = html + '<li><span style="font-weight:bold;">Other Phone: </span>' + item.other_phone + '</li>'
			html = "<ul>" + html + "</ul>"
		return html
	contact_info.allow_tags = True
		
		
	
	def candidacies(self, item):
		html = ''
		
		if item.candidacy_set.all():
			for candidacy in item.candidacy_set.all():
				html = html + '<li style="list-style-type: disc; list-style-position: inside; "><a href="/admin/human_resources/candidacy/' + str(candidacy.id) + '/">' + str(candidacy) + '</a></li>'
			html = '<ul>' + html + '</ul>'
		
		return html
	candidacies.allow_tags = True
	
	inlines = [WebLinkInline, FileInline]
	list_filter = ('status', )
	list_display = ('name', 'status', 'contact_info', 'candidacies', 'person_files')
	
	fieldsets = (
		('', {
			'fields': ('status',)
		}),
		('General Info', {
			'fields': ('first_name','middle_name', 'last_name',),
		}),
		('Contact Info', {
			'fields': ('email','mobile_phone', 'other_phone',),
		}),
		('Social Media', {
			'fields': ('twitter_handle','facebook_url', 'google_plus_url', 'linked_in_url',),
		}),
		('Address', {
			'fields': ('address','address_two', 'city', 'state', 'zip_code'),
		}),
	)
	



class CandidacyInline(HRTabularInline):
	model = Candidacy
	extra = 0
	fields = ('job_opportunity', 'person', 'rank')


class QualificationInline(HRTabularInline):
	model = Qualification
	extra = 0

class NiceToHaveInline(HRTabularInline):
	model = NiceToHave
	extra = 0


class ResponsibilityInline(HRTabularInline):
	model = Responsibility
	extra = 0

class PositionAdmin(HRAdmin):
	
	def changelist_view(self, request, extra_context=None):
		try:
			test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
			
			if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('status__exact'):
				path = request.path
				return HttpResponseRedirect(request.path + '?status__exact=1')
		except: pass # no referrer
		return super(PositionAdmin, self).changelist_view(request, extra_context=extra_context)
	
	
	def position_responsibilities(self, item):
		html = ''
		
		if item.responsibilities.all():
			for role in item.responsibilities.all():
				html = html + '<li style="list-style-type: disc; list-style-position: inside; "><a href="/admin/human_resources/role/' + str(role.id) + '/">' + str(role) + '</a></li>'
			html = '<ul>' + html + '</ul>'
		
		return html
	position_responsibilities.allow_tags = True
	
	inlines = [ResponsibilityInline, QualificationInline, NiceToHaveInline]
	list_display = ('name', 'private_description', 'position_responsibilities', 'importance')
	fieldsets = (
		('General Info', {
			"fields": ('name', 'importance', 'private_description', 'public_description'),
		}),
	)



class JobOpportunityAdmin(HRAdmin):
	
	def contract_types_available(self, item):
		html = ""
		if item.contract_types.exists():
			types_chain = chain(item.contract_types.all())
			
			while True:
				try:
					elem = types_chain.next()
					html = html + elem.name + ", "
				except StopIteration:
					html = html[:-2] # account for ' ' and ','
					break;
		return html
	contract_types_available.allow_tags = True
	
	filter_horizontal = ('contract_types','benefits')
	inlines = [CandidacyInline]
	list_display = ('position', 'location', 'contract_types_available', 'status', 'published_status')
	list_filter = ('published_status', 'status','contract_types', 'position',)
	fieldsets = (
		('', {
			"fields": ('published_status', 'status',),
		}),
		('General Info', {
			"fields": ('position','location',),
		}),
		('Deal Info', {
			"fields":  ('pay', 'contract_types', 'benefits'),
		}),
	)

class InterviewInline(HRTabularInline):
	model = Interview
	extra = 0


class EvaluationAdmin(admin.ModelAdmin):
	
	def changelist_view(self, request, extra_context=None):
		try:
			test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
			
			if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('status__exact'):
				path = request.path
				return HttpResponseRedirect(request.path + '?status__exact=1')
		except: pass # no referrer
		return super(EvaluationAdmin, self).changelist_view(request, extra_context=extra_context)
	
	
	def qualifications(self, item):
		html = ''		
		# loop through all qualifications for this evaluation's candidacy's
		# job opportunity
		
		relevant_responsibilities = item.candidacy.job_opportunity.position.responsibilities.all()
		
		qualifications = []
		
		if relevant_responsibilities:
			for role in relevant_responsibilities:
				if role.qualifications.all():
					for q in role.qualifications.all():
						
						if q in item.satisfied_qualifications.all():
							has_q = True
						else:
							has_q = False
							
						q_dic = {
							"qualification": q,
							"has_qualification": has_q
						}
						qualifications.append(q_dic)
		
			for q_dict in qualifications:
				if q_dict['has_qualification']:
					img_src = '/dev_media/grappelli/img/admin/icon-yes.gif'
				else:
					img_src = '/dev_media/grappelli/img/admin/icon-no.gif'
				html = html + '<li style="margin-bottom:10px;"><img style="margin-right: 5px; " src="' + img_src + '" />' + q_dict['qualification'].description + '</li>'
			
			html = '<ul>' + html + '</ul>'
		
		return html
	qualifications.allow_tags = True
	
	def nice_to_haves(self, item):
		html = ''
		
		relevant_responsibilities = item.candidacy.job_opportunity.position.responsibilities.all()
		
		nice_to_haves = []
		
		if relevant_responsibilities:
			for role in relevant_responsibilities:
				if role.nice_to_haves.all():
					for n in role.nice_to_haves.all():
						
						if n in item.satisfied_nice_to_haves.all():
							has_n = True
						else:
							has_n = False
							
						n_dic = {
							"nice_to_have": n,
							"has_nice_to_have": has_n
						}
						nice_to_haves.append(n_dic)
		
			for n_dict in nice_to_haves:
				if n_dict['has_nice_to_have']:
					img_src = '/dev_media/grappelli/img/admin/icon-yes.gif'
				else:
					img_src = '/dev_media/grappelli/img/admin/icon-no.gif'
				html = html + '<li style="margin-bottom:10px;"><img style="margin-right: 5px; " src="' + img_src + '" />' + n_dict['nice_to_have'].description + '</li>'
			
			html = '<ul>' + html + '</ul>'
	
		return html
	nice_to_haves.allow_tags = True
	
	def person(self, item):
		return item.candidacy.person
	person.admin_order_field = 'candidacy__person'
	
	def job_opportunity(self, item):
		return '<a href="/admin/human_resources/jobopportunity/' + str(item.candidacy.job_opportunity.id) + '/">' + str(item.candidacy.job_opportunity) + '</a>'
	job_opportunity.allow_tags = True
	job_opportunity.admin_order_field = 'candidacy__job_opportunity'
	
	def rank(self, item):
		return item.candidacy.rank
	rank.admin_order_field = 'candidacy__rank'
	
	inlines = [InterviewInline]
	list_filter = ('status', 'candidacy__job_opportunity', 'candidacy__person', 'candidacy__rank')
	list_display = ('person', 'rank', 'job_opportunity', 'qualifications', 'nice_to_haves', 'status')
	add_form = EvaluationAddForm
	filter_horizontal = ('satisfied_qualifications', 'satisfied_nice_to_haves')
	change_form = EvaluationChangeForm
	
	def get_form(self, request, obj=None, **kwargs):
		"""Use separate form for adding and changing evaluation objects
		because we need to know the Candidacy in question before presenting
		a list of qualifications that can be chosen for satisfaction"""
		
		defaults = {}
		
		if obj is None:
			defaults.update({
				'form': self.add_form,
			})
		else:
			defaults.update({
				'form': self.change_form,
			})
		
		defaults.update(kwargs)
		
		return super(EvaluationAdmin, self).get_form(request, obj, **defaults)
	
	def response_add(self, request, obj, post_url_continue='../%s/'):
		if '_addanother' not in request.POST and '_popup' not in request.POST:
			request.POST['_continue'] = 1
		return super(EvaluationAdmin, self).response_add(request, obj, post_url_continue)
	


admin.site.register(ContractType)
admin.site.register(Benefit)
admin.site.register(JobOpportunity, JobOpportunityAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Person, PersonAdmin)