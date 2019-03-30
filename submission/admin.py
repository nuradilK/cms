import nested_admin
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import redirect

from .models import Submission, RunInfo
from .tasks import evaluate_submission


class RunInfoInline(nested_admin.NestedTabularInline):
    model = RunInfo
    extra = 0
    fields = ['test', 'message', 'time', 'get_short_test_input', 'get_short_output', 'get_short_test_output',
              'get_view_link']
    readonly_fields = ['test', 'message', 'time', 'get_short_test_input', 'get_short_output', 'get_short_test_output',
                       'get_view_link']
    classes = ['collapse']
    verbose_name_plural = 'Execution Details'
    verbose_name = 'Execution Details'

    def get_view_link(self, run_info):
        view_link = '<a href="%s" target="popup">View</a>'\
                    % reverse('admin:submission_runinfo_change', args=[run_info.pk])
        return mark_safe(view_link)
    get_view_link.short_description = "View Link"

    def short(self, text):
        short = text
        if len(short) > 100:
            short = short[:100] + '...'
        return short

    def get_short_test_input(self, run_info):
        return self.short(run_info.test.input)
    get_short_test_input.short_description = "Input"

    def get_short_output(self, run_info):
        return self.short(run_info.output)
    get_short_output.short_description = "Output"

    def get_short_test_output(self, run_info):
        return self.short(run_info.test.output)
    get_short_test_output.short_description = "Jury Output"

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SubmissionAdmin(nested_admin.NestedModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['id', 'is_invocation']
        }),
        (None, {
            'fields': ['participant', 'problem', 'contest']
        }),
        (None, {
            'fields': ['sent_date', 'get_language_description']
        }),
        (None, {
            'fields': ['message', 'current_test', 'points']
        }),
        ('Source', {
            'fields': ['get_pretty_source'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['id', 'is_invocation', 'participant', 'problem', 'contest', 'sent_date',
                       'get_language_description', 'message', 'current_test', 'points', 'get_pretty_source']

    inlines = [RunInfoInline]

    def get_pretty_source(self, sub):
        # TODO fix code rendering issue
        return mark_safe('<pre><code>%s</code></pre>' % sub.source)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_rejudge_button'] = True
        submissions = Submission.objects.filter(pk=object_id)
        if not submissions or submissions.first().status == Submission.STATUS.IN_QUEUE \
                or submissions.first().status == Submission.STATUS.COMPILING \
                or submissions.first().status == Submission.STATUS.TESTING:
            extra_context['show_rejudge_button'] = False
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def response_change(self, request, submission):
        if "_rejudge" in request.POST:
            evaluate_submission.delay(submission.pk)
            self.message_user(request, "Submission evaluation has started")
            return redirect('.')

        return super().response_change(request, submission)

    def has_module_permission(self, request):
        return False


class RunInfoAdmin(nested_admin.NestedModelAdmin):
    fields = ['submission', 'test', 'status', 'time', 'get_test_input', 'output', 'get_test_output']
    readonly_fields = ['submission', 'test', 'status', 'time', 'get_test_input', 'output', 'get_test_output']

    def get_test_input(self, run_info):
        return run_info.test.input
    get_test_input.short_description = 'Input'

    def get_test_output(self, run_info):
        return run_info.test.output
    get_test_output.short_description = 'Jury Output'

    def has_module_permission(self, request):
        return False


admin.site.register(Submission, SubmissionAdmin)
admin.site.register(RunInfo, RunInfoAdmin)
