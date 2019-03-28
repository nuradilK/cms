from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from contest.models import Contest


class PolygonAccount(models.Model):
    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Problem(models.Model):
    class STATUS:
        IN_PROCESS = 0
        READY = 1
        FAILED = 2

    problem_id = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=100, unique=True)
    testset_name = models.CharField(max_length=100, default="tests")
    checker = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    status = models.SmallIntegerField(default=STATUS.IN_PROCESS)
    invocation_pk = models.CharField(max_length=100, blank=True)

    polygon_account = models.ForeignKey(PolygonAccount, on_delete=None)
    contest = models.ManyToManyField(Contest, blank=True)

    def __str__(self):
        if hasattr(self, 'statement'):
            return str(self.problem_id) + '-' + str(self.statement.name)
        else:
            return str(self.problem_id)

    def get_status_message(self):
        if self.status == Problem.STATUS.IN_PROCESS:
            return 'In process...'
        if self.status == Problem.STATUS.READY:
            return 'Ready'
        return 'Failed'

    get_status_message.short_description = 'Status'

    def get_title(self):
        if hasattr(self, 'statement'):
            return str(self.statement.name)
        return 'N/A'

    get_title.short_description = 'Title'


class Subtask(models.Model):
    subtask_id = models.AutoField(primary_key=True)
    score = models.IntegerField(default=0)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.description


class Test(models.Model):
    input = models.TextField()
    output = models.TextField(blank=True)
    test_id = models.IntegerField()
    in_statement = models.BooleanField(default=False)
    subtask = models.ForeignKey(Subtask, on_delete=models.CASCADE, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.problem.problem_id) + '-' + str(self.test_id)

    class Meta:
        order_with_respect_to = 'test_id'


class Statement(models.Model):
    legend = models.TextField(blank=True)
    input = models.TextField(blank=True)
    output = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    name = models.CharField(max_length=100, blank=True)
    time_limit = models.IntegerField(blank=True)
    memory_limit = models.IntegerField(blank=True)
    input_file = models.CharField(max_length=100, blank=True)
    output_file = models.CharField(max_length=100, blank=True)

    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.name)


from .tasks import process_problem as process_problem_task


@receiver(post_save, sender=Problem)
def process_problem(sender, instance, created, **kwargs):
    if created:
        process_problem_task.delay(instance.pk)
