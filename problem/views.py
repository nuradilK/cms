from django.shortcuts import render, get_object_or_404
from .models import Problem
from contest.models import Contest


def problem_page(request, contest_pk, problem_pk):
    contest = get_object_or_404(Contest, pk=contest_pk)
    problem = get_object_or_404(Problem, problem_id=problem_pk, contest=contest)

    context = {
        'statement': problem.statement,
        'samples': problem.test_set.filter(in_statement=True),
    }

    return render(request, 'problem/problem.html', context)
