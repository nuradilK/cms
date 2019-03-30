from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


def get_next_short_name(short_name):
    pos = len(short_name) - 1
    for ch in reversed(short_name):
        if ch != 'Z' and ch != 'z':
            break
        pos -= 1

    if pos == -1:
        return 'A' * (len(short_name) + 1)

    next_short_name = short_name[:pos]
    next_short_name += chr(ord(short_name[pos]) + 1)
    next_short_name += 'A' * (len(short_name) - pos - 1)

    return next_short_name


class Contest(models.Model):
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        order_with_respect_to = 'title'

    def __str__(self):
        return self.title

    def get_problem_short_name(self):
        problem_infos = self.probleminfo_set.extra(select={'length': 'Length(short_name)'}).order_by(
            'length',
            'short_name'
        )

        if problem_infos:
            return get_next_short_name(problem_infos.last().short_name)
        return 'A'


class Participant(models.Model):
    points = models.IntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
