import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import PhoneNumberField, USStateField

try:
	from django.conf import settings
	HR_UPLOAD_TO = settings.HR_UPLOAD_TO

except AttributeError:
	HR_UPLOAD_TO = settings.MEDIA_ROOT

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
	
	PERSON_STATUS_CHOICES = (
		(0, "Of Interest"),
		(1, "Applicant"),
		(2, "Former Applicant"),
		(3, "Employee"),
		(4, "Former Employee"),
		(5, "Independent Contractor"),
		(6, "Former Independent Contractor"),
		(7, "Intern"),
		(8, "Former Intern"),
	)
	
	status = models.IntegerField(choices=PERSON_STATUS_CHOICES, default=0)
	
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
	facebook_url = models.URLField("Facebook URL", verify_exists=True, blank=True)
	linked_in_url = models.URLField("LinkedIn URL", verify_exists=True, blank=True)
	
	class Meta:
		verbose_name_plural = 'people'
		ordering = ('-last_name',)
	
	def __unicode__(self):
		return "%s %s (%s)" %(self.first_name, self.last_name, self.get_status_display())



class PersonNote(HRModel):
	author = models.ForeignKey(User)
	person = models.ForeignKey("Person", related_name="notes")
	date_and_time = models.DateTimeField("Date & Time", default=datetime.datetime.now)
	note = models.TextField()

	def __unicode__(self):
		return u'%s' %(self.date_and_time)

	class Meta:
		ordering = ('-date_and_time',)


class WebLink(HRModel):
	person = models.ForeignKey("Person")
	name = models.CharField(max_length=25)
	url = models.URLField()

	def __unicode__(self):
		return self.name
	
	class Meta:
		ordering = ('name',)
		unique_together = ('person', 'name', 'url')

class File(HRModel):
	person = models.ForeignKey("Person", related_name="files")
	name = models.CharField(max_length=25)
	person_file = models.FileField("File", upload_to=HR_UPLOAD_TO+"/person_files")
	
	def __unicode__(self):
		return "%s: %s" %(self.person, self.name)
	
	class Meta:
		unique_together = ('person', 'name')

class Qualification(HRModel):
	position = models.ForeignKey("Position", related_name="qualifications")
	description = models.CharField(max_length=250)

	def __unicode__(self):
		if len(self.description) > 15:
			return "%s" %(self.description[:15] + '...')
		else:
			return self.description
	
	class Meta:
		unique_together = ('description', 'position')
		ordering = ('position__name',)


class NiceToHave(HRModel):
	position = models.ForeignKey("Position", related_name="nice_to_haves")
	description = models.CharField(max_length=250)

	def __unicode__(self):
		if len(self.description) > 15:
			return "%s" %(self.description[:15] + '...')
		else:
			return self.description
	
	class Meta:
		unique_together = ('description', 'position')


class Responsibility(HRModel):
	position = models.ForeignKey("Position", related_name="responsibilities")
	description = models.CharField(max_length=250)
	
	def __unicode__(self):
		if len(self.description) > 15:
			return "%s" %(self.description[:15] + '...')
		else:
			return self.description
	
	class Meta:
		verbose_name_plural = 'responsibilities'
		unique_together = ('position', 'description')


class Position(HRModel):
	
	name = models.CharField(max_length=75, unique=True)
	
	importance = models.PositiveSmallIntegerField(choices=IMPORTANCE_CHOICES, blank=True, null=True)
 	private_description = models.TextField("Why it's important", blank=True, help_text="This is private and never displayed to the public via the website.")
	public_description = models.TextField(blank=True, help_text="This is the public description displayed via the website.")
	
	class Meta:
		ordering = ('-importance',)
		
	def save(self):
		"""
		When saving a position, considering changing the evluation status of all its related 
		job opportunity's evaluations to status="Candidacy closed"
		
		"""
		super(Position, self).save()
	
	def __unicode__(self):
		return "%s" %(self.name)

class Benefit(HRModel):
	name = models.CharField(max_length=125, unique=True)
	
	class Meta:
		ordering = ('name',)
	
	def __unicode__(self):
		return self.name

class ContractType(HRModel):
	name = models.CharField(max_length=35, unique=True)
	
	class Meta:
		ordering = ('name',)
	
	def __unicode__(self):
		return self.name

class JobOpportunity(HRModel):
	POSITION_STATUS = (
		(1, "Open"),
		(2, "Filled"),
		(3, "Closed"),
	)
	
	OPPORTUNITY_STATUS_CHOICES = (
		(1, 'Unpublished'),
		(2, 'Published'),
	)
	
	"""
	CONTRACT_TYPES = (
		(0, "Employee - Full-Time"),
		(1, "Independent Contractor - Full-Time"),
		(2, "Employee - Part-Time"),
		(3, "Independent Contractor - Part-Time"),
		(4, "Internship - Full-Time"),
		(5, "Internship - Part-Time"),
	)
	"""
	status = models.PositiveSmallIntegerField(choices=POSITION_STATUS, default=1)
	published_status = models.PositiveSmallIntegerField(choices=OPPORTUNITY_STATUS_CHOICES, default=1)
	pay = models.CharField(max_length=125, blank=True)
	benefits = models.ManyToManyField("Benefit", blank=True, null=True)
	position = models.ForeignKey("Position", related_name="job_opportunities")
	location = models.CharField(max_length=150, default="Tustin, CA (Orange County)")
	contract_types = models.ManyToManyField("ContractType")
	
	def __unicode__(self):
		return "%s - %s" %(self.position, self.location)
	
	class Meta:
		verbose_name_plural = 'job opportunities'


class Candidacy(HRModel):
	job_opportunity = models.ForeignKey("JobOpportunity")
	person = models.ForeignKey("Person", related_name="candidacy_set")
	rank = models.PositiveSmallIntegerField(choices=IMPORTANCE_CHOICES, blank=True, null=True)
	
	class Meta:
		ordering = ('-rank',)
		verbose_name_plural = 'candidacies'
		unique_together = ('person', 'job_opportunity')
	
	def __unicode__(self):
		return "%s Candidacy: %s" %(self.job_opportunity, self.person)


class Interview(HRModel):
	INTERVIEW_TYPE = (
		(0, "Online"),
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