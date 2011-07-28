from django.contrib import admin

from hr.models import JobOpportunity, NiceToHaves, Candidate, Position, Qualification, Role, ContractType, Evaluation, Interview
from hr.forms import EvaluationAddForm

class HRAdmin(admin.ModelAdmin):
	readonly_fields = ('date_added', 'date_modified')


class HRTabularInline(admin.TabularInline):
	readonly_fields = ('date_added', 'date_modified')

class CandidateInline(HRTabularInline):
	model = Candidate
	extra = 0	


class QualificationInline(HRTabularInline):
	model = Qualification
	extra = 0

class NiceToHavesInline(HRTabularInline):
	model = NiceToHaves
	extra = 0


class RoleAdmin(HRAdmin):
	inlines = [QualificationInline, NiceToHavesInline]
	list_display = ('name', 'position', 'description')

class PositionAdmin(HRAdmin):
	
	def position_roles(self, item):
		html = ''
		
		if item.roles.all():
			for role in item.roles.all():
				html = html + '<li style="list-style-type: disc; list-style-position: inside; ">' + str(role) + '</li>'
			html = '<ul>' + html + '</ul>'
		
		return html
	position_roles.allow_tags = True
	
	filter_horizontal = ('roles',)
	list_filter = ('status','roles')
	list_display = ('name', 'private_description', 'position_roles', 'importance', 'status')
	fieldsets = (
		('', {
			"fields": ('status','importance', 'private_description'),
		}),
		('General Info', {
			"fields": ('name', 'roles', 'position_type', 'public_description'),
		}),
	)



class JobOpportunityAdmin(HRAdmin):
	
	inlines = [Candidate]
	list_display = ('position', 'status')
	list_filter = ('status','contract_type', 'position',)
	fieldsets = (
		('', {
			"fields": ('status',),
		}),
		('General Info', {
			"fields": ('position','location', 'contract_type'),
		}),
	)

class InterviewInline(HRAdmin):
	model = Interview
	extra = 0


class EvaluationAdmin(HRAdmin):
	
	inlines = [InterviewInline]
	
	add_form = EvaluationAddForm
	
	def form(self, request, obj=None, **kwargs):
		"""Use separate form for adding and changing evaluation objects
		because we need to know the candidate in question before presenting
		a list of qualifications that can be chosen for satisfaction"""
		
		defaults = {}
		
		if obj is None:
			defaults.update({
				'form': self.add_form,
			})
		
		defaults.update(kwargs)
		
		return super(EvaluationAdmin, self).get_form(request, obj, **defaults)
	
	def formfield_for_manytomany(self, db_field, request, **kwargs):
		"""Limit qualifications for an evaluation to those that are related
		to the job opportunity position at hand"""

		if db_field.name == "satisfied_qualifications":
			kwargs["queryset"] = Qualification.objects.filter(position=self.candidate.position)
		return super(Evaluation, self).formfield_for_manytomany(db_field, request, **kwargs)
	


admin.site.register(ContractType)
admin.site.register(JobOpportunity, JobOpportunityAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Evaluation, EvaluationAdmin)