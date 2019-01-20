from celery import shared_task
from .models import Submission

@shared_task
def evaluate_submission(sub_pk):
	""" Evaluate or re-evaluate submission """
	
	sub = Submission.objects.get(pk=sub_pk)

	sub.status = Submission.STATUSES['COMPILING']
	sub.save()

	# TODO Compiling stuff
	
	sub.status = Submission.STATUSES['TESTING']
	sub.save()

	# TODO Testing stuff
	# for test in self.problem.test_set.all()
	# 	result = sandbox.run(self.source, test.input, test.output, self.problem.time_limit, self.problem.memory_limit, self.checker)

	sub.status = Submission.STATUSES['FINISHED']
	sub.save()