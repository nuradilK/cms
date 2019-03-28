from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.shortcuts import redirect

from .models import Problem, Test, Statement, PolygonAccount, Subtask
from .tasks import process_problem

import nested_admin


class TestInline(nested_admin.NestedTabularInline):
    model = Test
    fields = ['test_id', 'get_short_input', 'get_short_output', 'in_statement', 'get_view_link', 'get_verdict']
    readonly_fields = ['test_id', 'get_short_input', 'get_short_output', 'in_statement', 'get_view_link', 'get_verdict']
    classes = ['collapse']
    ordering = ['test_id']

    def get_view_link(self, test=None):
        view_link = '<a href="%s" target="popup">View</a>' % reverse('admin:problem_test_change', args=[test.pk])
        return mark_safe(view_link)
    get_view_link.short_description = "View Link"

    def get_verdict(self, test=None):
        problem = test.problem
        runinfo_set = test.runinfo_set.filter(submission__pk=problem.invocation_pk)
        if not runinfo_set:
            return 'N/A'
        return runinfo_set.first().message()
    get_verdict.short_description = 'Execution Verdict'

    def short(self, text):
        short = text
        if len(short) > 100:
            short = short[:100] + '...'
        return short

    def get_short_input(self, test=None):
        return self.short(test.input)
    get_short_input.short_description = "Input"

    def get_short_output(self, test=None):
        return self.short(test.output)
    get_short_output.short_description = "Output"

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SubtaskInline(nested_admin.NestedStackedInline):
    model = Subtask
    inlines = [TestInline]
    classes = ['collapse']

    fields = ['description', 'score']
    readonly_fields = ['description', 'score']

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StatementInline(nested_admin.NestedStackedInline):
    model = Statement
    fields = ['name', 'time_limit', 'memory_limit', 'input_file', 'output_file', 'legend', 'input', 'output',
              'notes']
    readonly_fields = ['name', 'time_limit', 'memory_limit', 'input_file', 'output_file', 'legend', 'input', 'output',
                       'notes']
    classes = ['collapse']

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProblemAdmin(nested_admin.NestedModelAdmin):
    list_display = ('problem_id', 'name', 'get_status_message')
    readonly_fields = ['get_status_message', 'get_checker', 'get_solution']
    inlines = [StatementInline, SubtaskInline]

    def get_fieldsets(self, request, problem=None):
        if problem is None:
            return [
                (None, {
                    'fields': ['name', 'problem_id', 'polygon_account', 'testset_name', 'contest'],
                }),
            ]
        return [
            (None, {
                'fields': ['name', 'get_status_message', 'contest']
            }),
            ('Polygon Info', {
                'fields': ['problem_id', 'polygon_account', 'testset_name'],
                'classes': ['collapse']
            }),
            ('Checker', {'fields': ['get_checker'], 'classes': ['collapse']}),
            ('Solution', {'fields': ['get_solution'], 'classes': ['collapse']}),
        ]

    def get_inline_instances(self, request, problem=None):
        inlines = super().get_inline_instances(request, problem)
        if not problem:
            inlines = []
        return inlines

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_reload_button'] = True
        problem = Problem.objects.filter(pk=object_id)
        if not problem or problem.first().status == Problem.STATUS.IN_PROCESS:
            extra_context['show_reload_button'] = False
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def response_change(self, request, problem):
        if "_reload" in request.POST:
            process_problem.delay(problem.pk)
            self.message_user(request, "Problem processing has started")
            return redirect('.')

        return super().response_change(request, problem)

    def response_add(self, request, obj, post_url_continue=None):
        self.message_user(request, "Problem processing has started")
        return super().response_add(request, obj, post_url_continue=post_url_continue)

    def get_checker(self, problem=None):
        if problem.pk:
            # TODO fix code rendering issue
            return mark_safe('<pre><code>%s</code></pre>' % problem.checker)
        return 'N/A'
    get_checker.short_description = 'Source'

    def get_solution(self, problem=None):
        if problem.pk:
            # TODO fix code rendering issue
            return mark_safe('<pre><code>%s</code></pre>' % problem.solution)
        return 'N/A'
    get_solution.short_description = 'Source'


class TestAdmin(nested_admin.NestedModelAdmin):
    fields = ['test_id', 'in_statement', 'input', 'output']
    readonly_fields = ['test_id', 'input', 'output', 'in_statement']

    def has_module_permission(self, request):
        return False


class SubtaskAdmin(nested_admin.NestedModelAdmin):
    def has_module_permission(self, request):
        return False


class StatementAdmin(nested_admin.NestedModelAdmin):
    def has_module_permission(self, request):
        return False


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Subtask, SubtaskAdmin)
admin.site.register(Statement, StatementAdmin)
admin.site.register(PolygonAccount)
