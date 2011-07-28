from django import forms

from hr.models import Evaluation

class EvaluationAddForm(forms.ModelForm):
	class Meta:
		model = Evaluation
		exclude = ('satisfied_qualifications',)
