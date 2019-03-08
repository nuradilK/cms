from django.contrib import admin

from . import models


class ProblemAdmin(admin.ModelAdmin):
    fields = ['problem_id', 'key', 'secret', 'testset_name', 'contest']
    list_display = ('problem_id', 'get_title', 'get_status_message')


admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Test)
admin.site.register(models.Statement)
