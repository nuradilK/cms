from django.shortcuts import render
from .models import Problem

def problem_page(request, pk):
    statement = Problem.objects.get(problem_id=pk).statement_set.first()
    return render(request, 'problem/problem.html', {'statement':statement})