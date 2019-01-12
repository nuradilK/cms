from django.shortcuts import render
from .models import problem

def problem_page(request, pk):
    return render(request, 'problem/problem.html', problem.objects.filter(problem_id=pk).first().getData())