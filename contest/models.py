from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Contest(models.Model):
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = 'title'


class Participant(models.Model):
    score = models.IntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
