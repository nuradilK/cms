from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Contest

def info(request, contest_id = 1):
	contest = get_object_or_404(Contest, pk=contest_id)
	if not contest.is_active:
		raise Http404("Contest is not active!")
	return render(request, 'contests/info.html', {'contest': contest})
