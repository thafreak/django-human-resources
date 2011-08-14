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
		
		qualifications_queryset = Qualification.objects.filter(position__pk=self.instance.id)
		nice_to_haves_queryset = NiceToHave.objects.filter(position__pk=self.instance.id)
		
		self.fields['satisfied_qualifications'].queryset = qualifications_queryset
		self.fields['satisfied_nice_to_haves'].queryset = nice_to_haves_queryset
	