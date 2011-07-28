import datetime

from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField, USStateField

IMPORTANCE_CHOICES = (
	(1, 1),
	(2, 2),
	(3, 3),
	(4, 4),
	(5, 5),
	(6, 6),
	(7, 7),
	(8, 8),
	(9, 9),
	(10, 10),
)

class HRModel(models.Model):
	date_added = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	
	class Meta:
		abstract = True
		ordering = ('-date_modified',)
	


class Person(HRModel):
	
	first_name = models.CharField(max_length=25)
	middle_name = models.CharField(max_length=25, blank=True)
	last_name = models.CharField(max_length=25)
	
	email = models.EmailField(blank=True)
	mobile_phone = PhoneNumberField(blank=True)
	other_phone = PhoneNumberField(blank=True)
	
	address = models.CharField(max_length=125, blank=True)
	address_two = models.CharField("Address 2", max_length=125, blank=True)
	city = models.CharField(max_length=50, blank=True)
	state = USStateField(blank=True)
	zip_code = models.CharField(max_length=5, blank=True)
	
	twitter_handle = models.SlugField(max_length=35, blank=True)
	google_plus_url = models.URLField("Google+ URL", verify_exists=True, blank=True)
	facebook_url = models.URLField(verify_exists=True, blank=True)
	linked_in_url = models.URLField(verify_exists=True, blank=True)
	
	class Meta:
		verbose_name_plural = 'people'
		ordering = ('-last_name',)
	
	def __unicode__(self):
		return self.first_name + " " + self.last_name


class WebLink(HRModel):
	person = models.ForeignKey("Person")
	name = models.CharField(max_length=25)
	url = models.URLField()

	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)
		unique_together = ('person', 'name', 'url')
	

class Qualification(HRModel):
	description = models.CharField(max_length=500)
	role = models.ForeignKey("Role", related_name="qualifications")

	def __unicode__(self):
		return "%s: %s" %(self.role, self.description[:15] + '...')
	
	class Meta:
		unique_together = ('description', 'role')
		ordering = ('role__name',)


class NiceToHave(HRModel):
	description = models.CharField(max_length=500)
	role = models.ForeignKey("Role", related_name="nice_to_haves")

	def __unicode__(self):
		return "%s: %s" %(self.role, self.description[:15] + '...')
	
	class Meta:
		unique_together = ('description', 'role')


class Role(HRModel):
	name = models.CharField(max_length=45, unique=True)
	description = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.name


class Position(HRModel):
	POSITION_STATUS = (
		(1, "Open"),
		(2, "Filled"),
		(3, "Closed"),
	)
	
	name = models.CharField(max_length=25)
	status = models.PositiveSmallIntegerField(choices=POSITION_STATUS, default=1)
	importance = models.PositiveSmallIntegerField(choices=IMPORTANCE_CHOICES, default=5)
 	private_description = models.TextField("Why it's important", blank=True)
	public_description = models.TextField(blank=True)
	roles = models.ManyToManyField("Role", blank=True, null=True)
	
	class Meta:
		ordering = ('-importance',)
		
	def save(self):
		"""
		When saving a position, considering changing the evluation status of all its related 
		job opportunity's evaluations to status="Candidacy closed"
		
		"""
		super(Position, self).save()
	
	def __unicode__(self):
		return "%s Position (%s)" %(self.name, self.get_status_display())


class ContractType(HRModel):
	name = models.CharField(max_length=35, unique=True)
	
	class Meta:
		ordering = ('name',)
	
	def __unicode__(self):
		return self.name

class JobOpportunity(HRModel):
	OPPORTUNITY_STATUS_CHOICES = (
		(1, 'unpublished'),
		(2, 'published'),
	)
	
	status = models.PositiveSmallIntegerField(choices=OPPORTUNITY_STATUS_CHOICES, default=1)
	position = models.ForeignKey("Position")
	location = models.CharField(max_length=150, default="Tustin, CA (Orange County)")
	contract_types = models.ManyToManyField("ContractType")
	
	def __unicode__(self):
		return "%s - %s" %(self.position, self.location)
	
	class Meta:
		verbose_name_plural = 'job opportunities'


class Candidacy(HRModel):
	job_opportunity = models.ForeignKey("JobOpportunity")
	person = models.ForeignKey("Person", related_name="candidacy_set")
	rank = models.PositiveSmallIntegerField(choices=IMPORTANCE_CHOICES, default=5)
	
	class Meta:
		ordering = ('rank',)
		verbose_name_plural = 'candidacies'
		unique_together = ('person', 'job_opportunity')
	
	def __unicode__(self):
		return "%s Candidacy: %s" %(self.job_opportunity, self.person)


class Interview(HRModel):
	INTERVIEW_TYPE = (
		(1, "Phone"),
		(2, "In-person"),
	)
	
	interview_type = models.PositiveSmallIntegerField(choices=INTERVIEW_TYPE)
	date = models.DateTimeField(default=datetime.datetime.now)
	notes = models.TextField(blank=True)
	evaluation = models.ForeignKey("Evaluation")
	
	def __unicode__(self):
		return "%s %s Interview (%s)" %(self.evaluation.candidacy, self.interview_type, self.date.strftime("%m/%d/%y"))

class Evaluation(HRModel):
	EVALUATION_STATUS_CHOICES = (
		(1, "In consideration"),
		(2, "Candidacy closed")
	)
		
	
	status = models.PositiveSmallIntegerField(choices=EVALUATION_STATUS_CHOICES, default=1)
	candidacy = models.ForeignKey("Candidacy")
	satisfied_qualifications = models.ManyToManyField("Qualification", blank=True, null=True)
	satisfied_nice_to_haves = models.ManyToManyField("NiceToHave", blank=True, null=True)
	
	
	def __unicode__(self):
		return "%s Evaluation for %s (%s)" %(self.candidacy.job_opportunity, self.candidacy.person, self.get_status_display())