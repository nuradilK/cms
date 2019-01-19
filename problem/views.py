from django.shortcuts import render, get_object_or_404
from .models import Problem
from contest.models import Contest

def problem_page(request, contest_id, pk):
    contest = get_object_or_404(Contest, pk=contest_id)
    problem = get_object_or_404(Problem, problem_id=pk, contest=contest)
    statement = problem.statement
    samples = problem.test_set.filter(in_statement=True)
    return render(request, 'problem/problem.html', {'statement':statement, 'samples': samples})