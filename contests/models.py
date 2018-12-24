from django.db import models
from django.utils import timezone

class Contest(models.Model):
	title = models.CharField(max_length=100)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.title
