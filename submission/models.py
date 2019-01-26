from django.db import models
from contest.models import Contest
from problem.models import Problem


class Submission(models.Model):
	class STATUS:
		IN_QUEUE = 0
		COMPILING = 1
		TESTING = 2
		FINISHED = 3

	class LANGUAGE:
		CPP17 = 0

	source = models.TextField(blank=True)
	language = models.SmallIntegerField(default=0)
	status = models.SmallIntegerField(default=0)

	contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return str(self.pk) + '-' + str(self.status)
