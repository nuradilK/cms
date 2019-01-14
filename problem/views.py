from django.shortcuts import render
from .models import Problem

def problem_page(request, pk):
    statement = Problem.objects.get(problem_id=pk).statement
    return render(request, 'problem/problem.html', {'statement':statement})