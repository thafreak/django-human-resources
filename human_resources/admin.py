from itertools import chain

from django.contrib import admin
from django.db.models import URLField, CharField
from django.http import HttpResponseRedirect
from django.core.cache import cache

import twitter

from human_resources.models import Person, WebLink, JobOpportunity, \
NiceToHave, Candidacy, Position, Qualification, Responsibility, \
ContractType, Evaluation, Interview, File, Benefit, PersonNote
from human_resources.forms import EvaluationAddForm, EvaluationChangeForm
from human_resources.widgets import WebLinkWidget, ExtraWideCharFieldWidget

try:
	import memcache
	memcache_present = True
except ImportError:
	memcache_present = False


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


class PersonNoteInline(HRTabularInline):
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == 'author':
			kwargs['initial'] = request.user
		return super(PersonNoteInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
	
	model = PersonNote
	extra = 0

class PersonAdmin(HRAdmin):
	
	TWITTER_CACHE_TIME = 60 * 5 # 5 min
	twitter_api = twitter.Api()
	
	def twitter(self, item):
		html = ''
		
		def construct_html():
			statuses = self.twitter_api.GetUserTimeline(item.twitter_handle)
			if statuses:
				latest_tweet = statuses[0].text
				latest_tweet_html = '<div style="font-weight:bold; margin-bottom:5px;">Latest Tweet:</div><div>'
				latest_tweet_html = latest_tweet_html + '<div style="margin-bottom:5px;">"' + latest_tweet + '"</div>'
				link_html = '<a target="_blank" href="http://twitter.com/#!/' + item.twitter_handle + '">@' + item.twitter_handle + '</a>'
				html = latest_tweet_html + link_html
			else:
				html = '<a target="_blank" href="http://twitter.com/#!/' + item.twitter_handle + '">@' + item.twitter_handle + '</a>'
			return html
		
		if item.twitter_handle:
			# try to get the latest tweet
			try:
				# try to access cached status
				if memcache_present:
					cache_key = 'twitter_status_html_for_' + str(item.id)
					
					# try to get cached html variable
					if cache.get(cache_key) is not None:
						html = cache.get(cache_key)
						
					else:
						html = construct_html()
						cache.set(cache_key, html, self.TWITTER_CACHE_TIME)
						
				else:
					html = construct_html()
					
			except twitter.TwitterError:
				html = '<span>Twitter user not found</span>'
		else:
			html = ''
		return html
	twitter.allow_tags = True
	
	
	def latest_note(self, item):
		def get_user_representation(user):
			if user.first_name or user.last_name:
				return user.first_name + " " + user.last_name
			else:
				return user.username
		
		if item.notes.all():
			latest_note = item.notes.all()[0]
			return '<span style="font-weight:bold;">' + get_user_representation(latest_note.author) + ' on ' + latest_note.date_and_time.strftime("%B %d, %Y") + ': </span>' + latest_note.note
		else:
			return ''
	latest_note.allow_tags = True
	
	def name(self, item):
		return u'%s, %s' %(item.last_name, item.first_name)
	name.admin_order_field = 'last_name'
	
	def person_files(self, item):
		html = ""
		if item.files.exists():
			for f in item.files.all():
				html = html + '<li><a target="_blank" href="' + f.person_file.url + '">&darr; ' + f.name + '</a></li>'
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
		
	def web_links(self,	item):
		html = ''
		
		for web_link in item.web_links.all():
			html = html + '<li><a target="_blank" href="' + web_link.url + '">' + web_link.name + '</a></li>'
		html = '<ul>' + html + '</ul>'
		return html
	web_links.allow_tags = True	
	
	def candidacies(self, item):
		html = ''
		
		if item.candidacy_set.all():
			for candidacy in item.candidacy_set.all():
				html = html + '<li style="list-style-type: disc; list-style-position: inside; "><a href="/admin/human_resources/jobopportunity/' + str(candidacy.job_opportunity.id) + '/">' + str(candidacy.job_opportunity) + '</a></li>'
			html = '<ul>' + html + '</ul>'
		
		return html
	candidacies.allow_tags = True
	
	inlines = [WebLinkInline, FileInline, PersonNoteInline]
	list_filter = ('status', )
	list_display = ('name', 'status', 'contact_info', 'candidacies', 'twitter', 'web_links', 'person_files', 'latest_note')
	
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
	formfield_overrides = {
		CharField: {'widget': ExtraWideCharFieldWidget},
	}

class NiceToHaveInline(HRTabularInline):
	model = NiceToHave
	extra = 0
	formfield_overrides = {
		CharField: {'widget': ExtraWideCharFieldWidget},
	}


class ResponsibilityInline(HRTabularInline):
	model = Responsibility
	extra = 0
	formfield_overrides = {
		CharField: {'widget': ExtraWideCharFieldWidget},
	}

class PositionAdmin(HRAdmin):
	'''
	def changelist_view(self, request, extra_context=None):
		try:
			test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
			
			if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('status__exact'):
				path = request.path
				return HttpResponseRedirect(request.path + '?status__exact=1')
		except: pass # no referrer
		return super(PositionAdmin, self).changelist_view(request, extra_context=extra_context)
	'''
	
	def public_job_description(self, item):
		if item.public_description:
			return item.public_description
		else:
			return ""
	public_job_description.allow_tags = True
	
	def position_responsibilities(self, item):
		html = ''
		
		if item.responsibilities.all():
			for role in item.responsibilities.all():
				html = html + '<li style="list-style-type: disc; list-style-position: inside; "><a href="/admin/human_resources/role/' + str(role.id) + '/">' + str(role.description) + '</a></li>'
			html = '<ul>' + html + '</ul>'
		
		return html
	position_responsibilities.allow_tags = True
	
	inlines = [ResponsibilityInline, QualificationInline, NiceToHaveInline]
	list_display = ('name', 'importance', 'private_description', 'public_job_description', 'position_responsibilities',)
	fieldsets = (
		('General Info', {
			"fields": ('name', 'importance', 'private_description', 'public_description'),
		}),
	)



class JobOpportunityAdmin(HRAdmin):
	
	def contract_types_available(self, item):
		html = ""
		if item.contract_types.exists():
			for c in item.contract_types.all():
				html = html + '<li>' + c.name + '</li>'
			html = '<ul>' + html + '</ul>'
		return html
	contract_types_available.allow_tags = True
	
	def benefits_offered(self, item):
		html = ""
		if item.benefits.exists():
			for b in item.benefits.all():
				html = html + '<li>' + b.name + '</li>'
			html = '<ul>' + html + '</ul>'
		return html
	benefits_offered.allow_tags = True
	
	filter_horizontal = ('contract_types','benefits')
	inlines = [CandidacyInline]
	list_display = ('position', 'location', 'pay', 'contract_types_available', 'benefits_offered', 'status', 'published_status')
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
		
		qualifications = []
		
		all_qualifications = item.candidacy.job_opportunity.position.qualifications.all()
		
		for q in all_qualifications:
						
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
		
		if qualifications:
			html = '<ul>' + html + '</ul>'
	
		return html
	qualifications.allow_tags = True
	
	def nice_to_haves(self, item):
		html = ''

		nice_to_haves = []
		
		all_nice_to_haves = item.candidacy.job_opportunity.position.nice_to_haves.all()
		
		for n in all_nice_to_haves:
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
		
		if nice_to_haves:
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
	
	def position(self, item):
		return '<a href="/admin/human_resources/position/ ' + str(item.candidacy.job_opportunity.position.id) + ' /">' + str(item.candidacy.job_opportunity.position) + '</a>'
	position.allow_tags = True
	
	def rank(self, item):
		return item.candidacy.rank
	rank.admin_order_field = 'candidacy__rank'
	
	raw_id_fields = ('candidacy', )
	related_lookup_fields = {
		'fk': ['candidacy']
	}
	
	inlines = [InterviewInline]
	list_filter = ('status', 'candidacy__job_opportunity', 'candidacy__job_opportunity__position', 'candidacy__person', 'candidacy__rank')
	list_display = ('person', 'rank', 'job_opportunity', 'position', 'qualifications', 'nice_to_haves', 'status')
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
	


class CandidacyAdmin(HRAdmin):
	list_display = ('person', 'job_opportunity', 'rank')
	list_filter = ('person', 'job_opportunity', 'rank')

admin.site.register(Candidacy, CandidacyAdmin)
admin.site.register(ContractType)
admin.site.register(Benefit)
admin.site.register(JobOpportunity, JobOpportunityAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Person, PersonAdmin)