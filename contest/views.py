from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import datetime

from .models import Contest

def info(request, contest_id = 1):
	if not request.user.is_authenticated:
		return redirect('login-page')
	contest = get_object_or_404(Contest, pk=contest_id)
	if not contest.is_active:
		raise Http404("Contest is not active!")
	context = {
		'contest': contest,
		'username': request.user.username,
		'current_time': datetime.datetime.now(),
	}
	return render(request, 'contests/info.html', context)
def login_page(request):
	if request.user.is_authenticated:
		return redirect('contest-info')
	return render(request, 'login.html')
def user(request):
	if request.user.is_authenticated:
		return redirect('contest-info')
	if request.method != 'POST':
		return redirect('contest-info')
	if not 'username' in request.POST:
		return redirect('contest-info')
	if not 'password' in request.POST:
		return redirect('contest-info')
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		return redirect('contest-info')
	else:
		return redirect('login-page')
def logout_page(request):
    logout(request)
    return redirect('login-page')