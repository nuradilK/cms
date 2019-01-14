from django.shortcuts import render
from .models import Problem

def problem_page(request, pk):
    return render(request, 'problem/problem.html', Problem.objects.filter(problem_id=pk).first().getData())