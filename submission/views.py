from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone

from .models import Submission
from .tasks import evaluate_submission
from .forms import SubmitForm


def test_submit(request, contest_pk):
    if not request.user.participant_set.filter(contest__pk=contest_pk):
        return HttpResponse("You are not registered for this contest")

    if request.method == "POST":
        form = SubmitForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.participant = request.user.participant_set.get(contest__pk=contest_pk)
            sub.sent_date = timezone.now()
            sub.save()

            evaluate_submission.delay(sub.pk)

            return redirect('submission-detail', pk=sub.pk)
    else:
        form = SubmitForm()

    return render(request, 'submission/test_submit.html', {'form': form})


def detail(request, pk):
    sub = get_object_or_404(Submission, pk=pk)

    if sub.participant.user != request.user:
        return HttpResponse("You are not allowed to see this page")

    status = sub.message()
    if sub.status == Submission.STATUS.TESTING:
        if sub.current_test != 0:
            status = 'Running on test ' + str(sub.current_test) + '...'
        else:
            status = 'Running...'

    runinfo_list = sub.runinfo_set.all()

    return render(request, 'submission/detail.html', {'sub': sub, 'status': status, 'runinfo_list':runinfo_list})
