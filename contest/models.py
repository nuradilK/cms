from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Contest(models.Model):
	title = models.CharField(max_length=100)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.title

	class Meta:
		order_with_respect_to = 'title'

class Participant(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
	score = models.IntegerField(default=0)
	contest = models.ManyToManyField(Contest, blank=True)

	def __str__(self):
		return self.user.username