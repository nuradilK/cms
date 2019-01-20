from django.shortcuts import render
from django.http import HttpResponse

from .models import Submission
from .tasks import evaluate_submission

def test_submit(request):
	sub = Submission.objects.create()
	evaluate_submission.delay(sub.pk)

	return HttpResponse("kek 2")
