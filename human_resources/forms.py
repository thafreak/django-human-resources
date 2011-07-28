from django import forms

from human_resources.models import Evaluation

class EvaluationAddForm(forms.ModelForm):
	class Meta:
		model = Evaluation
		exclude = ('satisfied_qualifications',)
