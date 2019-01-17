from django.shortcuts import render, get_object_or_404
from .models import Problem

def problem_page(request, pk):
    problem = get_object_or_404(Problem, problem_id=pk)
    statement = problem.statement
    samples = problem.test_set.filter(in_statement=True)
    return render(request, 'problem/problem.html', {'statement':statement, 'samples': samples})