from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

from contest.models import Contest


class Problem(models.Model):
    class STATUS:
        IN_PROCESS = 0
        READY = 1
        FAILED = 2

    problem_id = models.CharField(default='', max_length=20)
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)
    testset_name = models.CharField(max_length=100, default="tests")
    contest = models.ManyToManyField(Contest, blank=True)
    checker = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    status = models.SmallIntegerField(default=STATUS.IN_PROCESS)

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


class Test(models.Model):
    input = models.TextField()
    output = models.TextField(blank=True)
    test_id = models.IntegerField()
    in_statement = models.BooleanField(default=False)

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.problem.problem_id) + '-' + str(self.test_id)

    class Meta:
        order_with_respect_to = 'test_id'


class Statement(models.Model):
    legend = models.TextField()
    input = models.TextField()
    output = models.TextField()
    notes = models.TextField()
    name = models.CharField(max_length=100)
    time_limit = models.IntegerField()
    memory_limit = models.IntegerField()
    input_file = models.CharField(max_length=100)
    output_file = models.CharField(max_length=100)

    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.name)


from .tasks import proceed_problem


@receiver(post_save, sender=Problem)
def get_problem_data(sender, instance, created, **kwargs):
    Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.IN_PROCESS)
    proceed_problem.delay(instance.pk, created)

