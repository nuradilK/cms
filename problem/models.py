from django.db import models
from contest.models import Contest
import requests
import time
import hashlib
from django.db.models.signals import post_save
from django.dispatch import receiver


class Problem(models.Model):
    problem_id = models.IntegerField(default=0)
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)
    testset_name = models.CharField(max_length=100, default="tests")
    contest = models.ManyToManyField(Contest, blank=True)

    def __str__(self):
        return str(self.problem_id) + '-' + str(self.statement.name)


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


def get_statement(params):
    api_url = "https://polygon.codeforces.com/api/"
    method = 'problem.statements'

    return requests.get(api_url + method, params).json()


def get_info(params, instance, cur_time):
    api_url = "https://polygon.codeforces.com/api/"
    method = 'problem.info'

    params['apiSig'] = '123456' + hashlib.sha512(str(
        '123456/problem.info?apiKey=' + instance.key + '&problemId=' + str(
            instance.problem_id) + '&time=' + cur_time + '#' + instance.secret).encode('utf-8')).hexdigest();
    return requests.get(api_url + method, params).json()


def get_test(params, instance, cur_time):
    api_url = "https://polygon.codeforces.com/api/"
    method = 'problem.tests'

    params['apiSig'] = 'ajkoi4' + \
                       hashlib.sha512(str('ajkoi4/problem.tests?apiKey=' + instance.key + '&problemId=' +
                                          str(instance.problem_id) + '&testset=' + instance.testset_name + '&time=' +
                                          cur_time + '#' + instance.secret).encode('utf-8')).hexdigest()
    params['testset'] = instance.testset_name
    return requests.get(api_url + method, params).json()


@receiver(post_save, sender=Problem)
def get_problem_data(sender, instance, created, **kwargs):
    cur_time = str(int(time.time()))
    params = {
        'apiKey': instance.key,
        'time': cur_time,
        'apiSig': '654321' + hashlib.sha512(str(
            '654321/problem.statements?apiKey=' + instance.key + '&problemId=' + str(
                instance.problem_id) + '&time=' + cur_time + '#' + instance.secret).encode('utf-8')).hexdigest(),
        'problemId': instance.problem_id,
    }

    statement = get_statement(params)
    info = get_info(params, instance, cur_time)
    tests = get_test(params, instance, cur_time)

    for i in tests['result']:
        if 'input' in i:
            cur_test = Test(input=i['input'], test_id=i['index'], in_statement=i['useInStatements'])
            if cur_test not in list(Test.objects.all()):
                instance.test_set.create(input=i['input'], test_id=i['index'], in_statement=i['useInStatements'])

    cur_statement = Statement(legend=statement['result']['russian']['legend'],
                              input=statement['result']['russian']['input'],
                              output=statement['result']['russian']['output'],
                              notes=statement['result']['russian']['notes'],
                              name=statement['result']['russian']['name'], time_limit=info['result']['timeLimit'],
                              memory_limit=info['result']['memoryLimit'], 
                              input_file=info['result']['inputFile'], output_file=info['result']['outputFile'])
    
    if created is False:
        Statement.objects.get(name=instance.statement.name).delete()
    instance.statement = cur_statement.save()
