import nested_admin
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Contest, Participant
from problem.models import Problem, ProblemInfo
from submission.models import Submission


class SubmissionInline(nested_admin.NestedTabularInline):
    model = Submission
    fields = ['get_id_as_view_link', 'get_username_as_view_link', 'sent_date', 'get_language_description', 'message',
              'points']
    readonly_fields = ['get_id_as_view_link', 'get_username_as_view_link', 'sent_date', 'get_language_description',
                       'message', 'points']
    classes = ['collapse']
    ordering = ['id']

    def get_id_as_view_link(self, submission):
        view_link = '<a href="%s" target="popup">%s</a>'\
                    % (reverse('admin:submission_submission_change', args=[submission.pk]), submission.id)
        return mark_safe(view_link)
    get_id_as_view_link.short_description = "ID"

    def get_username_as_view_link(self, submission):
        view_link = '<a href="%s" target="popup">%s</a>' \
                    % (reverse('admin:auth_user_change', args=[submission.participant.user.pk]),
                       submission.participant.user.username)
        return mark_safe(view_link)
    get_username_as_view_link.short_description = "Participant"

    def has_add_permission(self, request, obj):
        return False


class ProblemInfoInline(nested_admin.NestedTabularInline):
    model = ProblemInfo
    extra = 0
    fields = ['short_name', 'get_problem_name_as_view_link', 'get_problem_statement_name', 'get_problem_id', 'get_problem_max_points']
    readonly_fields = ['get_problem_name_as_view_link', 'get_problem_statement_name', 'get_problem_id', 'get_problem_max_points']
    ordering = ['short_name', 'problem__name']
    classes = ['collapse']
    verbose_name = 'PROBLEM'
    verbose_name_plural = 'PROBLEMS'
    inlines = [SubmissionInline]

    def get_problem_name_as_view_link(self, problem_info):
        view_link = '<a href="%s" target="popup">%s</a>' \
                    % (reverse('admin:problem_problem_change', args=[problem_info.problem.pk]),
                       problem_info.problem.name)
        return mark_safe(view_link)
    get_problem_name_as_view_link.short_description = 'Name'

    def get_problem_statement_name(self, problem_info):
        return problem_info.problem.statement.name
    get_problem_statement_name.short_description = 'Name in Statements'

    def get_problem_id(self, problem_info):
        return problem_info.problem.problem_id
    get_problem_id.short_description = 'Polygon ID'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(problem__status=Problem.STATUS.READY)

    def has_add_permission(self, request, obj):
        return False


class ParticipantInline(nested_admin.NestedTabularInline):
    model = Participant
    extra = 0
    fields = ['get_username_as_view_link', 'points']
    readonly_fields = ['get_username_as_view_link', 'points']
    classes = ['collapse']
    ordering = ['points', 'user__username']

    def get_username_as_view_link(self, participant):
        view_link = '<a href="%s" target="popup">%s</a>' \
                    % (reverse('admin:auth_user_change', args=[participant.user.pk]), participant.user.username)
        return mark_safe(view_link)
    get_username_as_view_link.short_description = "Username"

    def has_add_permission(self, request, obj):
        return False


class ContestAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'is_active']
    fields = ['title', 'start_time', 'end_time', 'is_active']
    inlines = [ProblemInfoInline, ParticipantInline]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        contest = Contest.objects.get(pk=object_id)
        users = User.objects.exclude(participant__contest=contest)
        problems = Problem.objects.filter(status=Problem.STATUS.READY).exclude(probleminfo__contest=contest)

        extra_context['users'] = users
        extra_context['problems'] = problems

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def response_change(self, request, contest):
        super().response_change(request, contest)

        if "users" in request.POST:
            users = request.POST.getlist('users')
            for user_pk in users:
                user = User.objects.get(pk=user_pk)
                if not user.participant_set.filter(contest=contest):
                    user.participant_set.create(contest=contest)

        if "problems" in request.POST:
            problems = request.POST.getlist('problems')
            for problem_id in problems:
                problem = Problem.objects.get(problem_id=problem_id)
                if not ProblemInfo.objects.filter(contest=contest, problem=problem):
                    ProblemInfo.objects.create(contest=contest, problem=problem,
                                               short_name=contest.generate_problem_short_name())

        return redirect('.')


admin.site.register(Contest, ContestAdmin)
