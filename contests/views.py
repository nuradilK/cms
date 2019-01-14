from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
from .models import Contest

@login_required(redirect_field_name='login-page')
def info(request, contest_id = 1):
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
	context = {}
	if request.user.is_authenticated:
		return redirect('contest-info')
	if request.method == 'POST':
		if not 'username' in request.POST:
			context['auth_msg'] = 'Do not have a username'
		elif not 'password' in request.POST:
			context['auth_msg'] = 'Do not have a password'
		else:
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('contest-info')
			else:
				context['auth_msg'] = 'Wrong credentials'
	if not 'auth_msg' in context:
		context['auth_msg'] = 'Enter your username and password'
	if request.user.is_authenticated:
		return redirect('contest-info')
	return render(request, 'login.html', context)

@login_required(redirect_field_name='login-page')
def logout_page(request):
    logout(request)
    return redirect('login-page')