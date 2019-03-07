from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import datetime
from .models import Contest, Participant


@login_required(redirect_field_name='login-page')
def info(request, contest_pk=1):
    contest = get_object_or_404(Contest, pk=contest_pk)
    if not contest.is_active:
        raise Http404("Contest is not active!")
    if not list(Participant.objects.filter(user=request.user, contest=contest)):
        return HttpResponse("You are not registered for this contest.")
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
        if 'username' not in request.POST:
            context['auth_msg'] = 'Do not have a username'
        elif 'password' not in request.POST:
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
    if 'auth_msg' not in context:
        context['auth_msg'] = 'Enter your username and password'
    if request.user.is_authenticated:
        return redirect('contest-info')
    return render(request, 'login.html', context)


@login_required(redirect_field_name='login-page')
def logout_page(request):
    logout(request)
    return redirect('login-page')


def ranking(request, contest_pk):
    cur_contest = get_object_or_404(Contest, pk=contest_pk)
    participants = list(Participant.objects.filter(contest__title=cur_contest.title).order_by('-score'))
    context = {
        'participants': participants,
    }
    return render(request, 'contests/ranking.html', context)
