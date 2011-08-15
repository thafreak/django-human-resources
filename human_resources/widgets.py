from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django import template
import os

class WebLinkWidget(forms.TextInput):
	def __init__(self, attrs={}):
		super(WebLinkWidget, self).__init__(attrs)
	
	def render(self, name, value, attrs=None):
		output = []
		attrs.update({
			'class': 'vTextField'
		})
		output.append(super(WebLinkWidget, self).render(name, value, attrs))
		
		if value:
			output.append('<a target="_blank" style="padding-left: 10px;" href="' + value + '">Go to URL &raquo;</a>')
		
		return mark_safe(u''.join(output))


class ExtraWideCharFieldWidget(forms.TextInput):
	def __init__(self, attrs={}):
		super(ExtraWideCharFieldWidget, self).__init__(attrs)
	
	def render(self, name, value, attrs=None):
		output = []
		attrs.update({
			'style': 'width:920px;',
		})
		output.append(super(ExtraWideCharFieldWidget, self).render(name, value, attrs))
		
		return mark_safe(u''.join(output))