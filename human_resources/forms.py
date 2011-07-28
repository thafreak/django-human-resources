from django import forms

from human_resources.models import Evaluation, Qualification, NiceToHave

class EvaluationAddForm(forms.ModelForm):
	
	class Meta:
		model = Evaluation
		fields = ('status','candidacy')


class EvaluationChangeForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super(EvaluationChangeForm, self).__init__(*args, **kwargs)
		
		# Limit qualifications for an evaluation to those that are related
		# to the job opportunity's position at hand 
		
		job_opportunity = self.instance.candidacy.job_opportunity
		job_opportunity_position = job_opportunity.position
		relevant_roles = job_opportunity_position.roles.all()
		
		# calcualte the ids for the relevant roles for use in querying
		# qualifications and nice to haves
		relevant_roles_ids = []
		qualifications_queryset = None
		nice_to_haves_queryset = None
		
		if relevant_roles:
			for role in relevant_roles:
				relevant_roles_ids.append(role.id)
				
			qualifications_queryset = Qualification.objects.filter(role__pk__in=relevant_roles_ids)
			nice_to_haves_queryset = NiceToHave.objects.filter(role__pk__in=relevant_roles_ids)
			
		else: 
			qualifications_queryset = Qualification.objects.empty()
			nice_to_haves_queryset = NiceToHave.objects.empty()
		
		self.fields['satisfied_qualifications'].queryset = qualifications_queryset
		self.fields['satisfied_nice_to_haves'].queryset = nice_to_haves_queryset
	