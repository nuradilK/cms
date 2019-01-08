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
	if 'auth_error' in request.session:
		context['auth_msg'] = request.session['auth_error']
		del request.session['auth_error']
	else:
		context['auth_msg'] = 'Enter your username and password'
	if request.user.is_authenticated:
		return redirect('contest-info')
	return render(request, 'login.html', context)

def user(request):
	if request.user.is_authenticated:
		return redirect('contest-info')
	if request.method != 'POST':
		request.session['auth_error'] = 'Wrong method to log in'
		return redirect('login-page')
	if not 'username' in request.POST:
		request.session['auth_error'] = 'Do not have a username'
		return redirect('login-page')
	if not 'password' in request.POST:
		request.session['auth_error'] = 'Do not have a password'
		return redirect('login-page')
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		return redirect('contest-info')
	else:
		request.session['auth_error'] = 'Wrong credentials'
		return redirect('login-page')

@login_required(redirect_field_name='login-page')
def logout_page(request):
    logout(request)
    return redirect('login-page')