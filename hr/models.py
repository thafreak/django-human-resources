import datetime

from django.db import models

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
	facebook_url = models.URLField(verify_exists=True, blank=True)
	linked_in_url = models.URLField(verify_exists=True, blank=True)
	
	website = models.URLField(blank=True)
	website_two = models.URLField("Website 2", blank=True)
	website_three = models.URLField("Website 3", blank=True)
	
	class Meta(Person.Meta):
		verbose_name_plural = 'people'


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
	description = models.TextField()
	role = models.ForeignKey("Role")

	def __unicode__(self):
		return "%s: %s" %(self.position, self.description[:15] + '...')


class NiceToHaves(HRModel):
	description = models.TextField()
	role = models.ForeignKey("Role")

	def __unicode__(self):
		return "%s: %s" %(self.position, self.description[:15] + '...')


class Role(HRModel):
	name = models.CharField(max_length=45)
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
		return "%s Position (%s)" %(self.name, self.status)


class ContractType(HRModel):
	name = models.CharField(max_length=35, unique=True)
	
	class Meta:
		ordering = ('name',)
	
	def __unicode__(self):
		return self.name

class JobOpportuntity(HRModel):
	OPPORTUNITY_STATUS_CHOICES = (
		(1, 'unpublished'),
		(2, 'published'),
	)
	
	status = models.PositiveSmallIntegerField(choices=OPPORTUNITY_STATUS_CHOICES, default=1)
	position = models.ForeignKey("Position")
	location = models.CharField(max_length=150, default="Tustin, CA (Orange County)")
	contract_type = models.ManyToManyField()
	
	def __unicode__(self):
		return "%s"
	


class Candidate(HRModel):
	position = models.ForeignKey("Position")
	person = models.ForeignKey("Person")
	rank = models.PositiveSmallIntegerField(choices=IMPORTANCE_CHOICES, default=5)
	
	class Meta:
		ordering = ('rank',)
	
	def __unicode__(self):
		return "%s Candidate: %s" %(self.position, self.person)


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
		return "%s %s Interview (%s)" %(self.evaluation.candidate, self.interview_type, self.date.strftime("%m/%d/%y"))

class Evaluation(HRModel):
	EVALUATION_STATUS_CHOICES = (
		(1, "In consideration"),
		(2, "Candidacy closed")
	)
		
	
	status = models.PositiveSmallIntegerField(choices=EVALUATION_STATUS_CHOICES, default=1)
	candidate = models.ForeignKey("Candidate")
	satisfied_qualifications = models.ManyToManyField("Qualification", blank=True, null=True)
	
	
	def __unicode__(self):
		return "%s Evaluation: %s (%s)" %(self.candidate.position, self.candidate, self.status)