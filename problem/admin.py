from django.contrib import admin

from . import models

admin.site.register(models.Problem)
admin.site.register(models.Test)