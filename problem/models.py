from django.db import models
import requests
import time
import hashlib

class problem(models.Model):
    problem_id = models.IntegerField(default=0)
    key = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)


    def __str__(self):
        return str(self.problem_id)

    def getData(self):
        api_url = "https://polygon.codeforces.com/api/"
        method = 'problem.statements'
        params = {
            'apiKey': self.key,
            'time': str(int(time.time())),
            'apiSig': '654321' + hashlib.sha512(str(
                '654321/problem.statements?apiKey='+self.key+'&problemId='+str(self.problem_id)+'&time=' + str(
                    int(time.time())) + '#' + self.secret).encode('utf-8')).hexdigest(),
            'problemId': self.problem_id,
        }
        statement = requests.get(api_url + method, params).json()

        method = 'problem.info'
        params = {
            'apiKey': self.key,
            'time': str(int(time.time())),
            'apiSig': '123456' + hashlib.sha512(str(
                '123456/problem.info?apiKey='+self.key+'&problemId='+str(self.problem_id)+'&time=' + str(
                    int(time.time())) + '#' + self.secret).encode('utf-8')).hexdigest(),
            'problemId': self.problem_id,
        }
        info = requests.get(api_url + method, params).json()

        st = statement['result']['russian']['legend']


        return {'statement': statement, 'info': info}

    # class Meta:
    #     order_with_respect_to = 'problem_id'
    #     data = {}
    #
    # @classmethod
    # def create(cls, problem_id, key, secret):
    #     new_problem = cls(problem_id=problem_id, key=key, secret=secret)
    #
    #     new_problem.data = problem.getData()

