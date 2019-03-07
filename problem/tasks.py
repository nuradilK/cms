import os
import requests
import time
import hashlib
import string
import random

from django.contrib.staticfiles.templatetags.staticfiles import static
from os.path import join as path_join
from celery import shared_task
from billiard import current_process
from sandbox.sandbox_manager import Sandbox
from .models import Statement, Test, Problem

api_url = "https://polygon.codeforces.com/api/"

def param_config(params):
    for key in list(params.keys()):
        if key not in ['apiKey', 'apiSig', 'time', 'problemId']:
            params.pop(key, None)

def gen_hash():
    return ''.join(random.choices(string.ascii_uppercase + string.digits+ string.ascii_lowercase, k=6))

def api_sig(method, secret, add):
    api_hash = gen_hash()
    signature = api_hash + '/' + method
    started = False
    for key, value in add:
        if started is False:
            signature = signature + '?'
        else:
            signature = signature + '&'
        signature = signature + key + '=' + value
        started = True
    signature = signature + '#' + secret
    return api_hash + hashlib.sha512(str(signature).encode('utf-8')).hexdigest()

def get_statement(params, instance, Time):
    param_config(params)
    method = 'problem.statements'
    my_params = [('apiKey', str(instance.key)), ('problemId', str(instance.problem_id)),
                ('time', Time)]
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    return requests.get(api_url + method, params).json()

def get_info(params, instance, Time):
    param_config(params)
    method = 'problem.info'
    my_params = [('apiKey', str(instance.key)), ('problemId', str(instance.problem_id)),
                ('time', Time)]
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    return requests.get(api_url + method, params).json()

def get_test(params, instance, Time):
    param_config(params)
    method = 'problem.tests'
    my_params = [('apiKey', str(instance.key)), ('problemId', str(instance.problem_id)),
                ('testset', instance.testset_name), ('time', Time)]
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    params['testset'] = instance.testset_name
    return requests.get(api_url + method, params).json()

def generator_code(params, instance, Time, scriptLine):
    param_config(params)
    name = scriptLine.split()[0] + '.cpp'
    method = 'problem.viewFile'
    my_params = [('apiKey', str(instance.key)), ('name', name), ('problemId', str(instance.problem_id)),
                ('time', Time), ('type', 'source')]
    params['type'] = 'source'
    params['name'] = name
    params['apiSig'] = api_sig(method, instance.secret, my_params)
    gen_code = requests.get(api_url + method, params).text
    return gen_code

def manual_test(instance, test):
    instance.test_set.create(input=test['input'], test_id=test['index'], in_statement=test['useInStatements'])

def script_test(instance, scriptLine, gen_source, gen_name, test):
    sandbox = Sandbox()
    sandbox.init(current_process().index)

    # CREATE FILES
    with open(path_join('.', 'problem', 'static', 'problem', 'testlib.h'), 'r') as testlib_file:
        testlib = testlib_file.read()
    sandbox.create_file(gen_name + '.cpp', str(gen_source), is_public=0)
    sandbox.create_file('testlib.h', str(testlib), is_public=0)
    
    # COMPILE
    sandbox.run_cmd('g++ -o ' + path_join('box', gen_name) + ' -std=c++11 -DONLINE_JUDGE ' + gen_name + '.cpp ' + 'testlib.h')

    # GET TEST
    out, err = sandbox.run_exec(exec=gen_name, cmd=' '.join(scriptLine.split()[1:]), dirs=[('/box', 'box', 'rw')], meta_file=sandbox.get_box_dir('meta'),
                     time_limit=10, memory_limit=128)
    
    instance.test_set.create(input=out.decode('utf-8'), test_id=test['index'], in_statement=test['useInStatements'])
    sandbox.cleanup()
    print(test['index'])

def create_tests(instance, params, Time, tests):
    for test in tests['result']:
        if test['manual'] is True:
            manual_test(instance, test)
        else:
            script_test(instance, test['scriptLine'], generator_code(params, instance, Time, test['scriptLine']), test['scriptLine'].split()[0], test)

@shared_task
def proceed_problem(prob_pk):
    print('Proceeding...')
    instance = Problem.objects.get(pk=prob_pk)
    Time = str(int(time.time()))
    params = {
        'apiKey': instance.key,
        'time': Time,
        'problemId': instance.problem_id,
    }
    statement = get_statement(params, instance, Time)
    print(statement)
    info = get_info(params, instance, Time)
    tests = get_test(params, instance, Time)
    create_tests(instance, params, Time, tests)
    cur_statement = Statement(problem = instance, legend=statement['result']['russian']['legend'],
                                  input=statement['result']['russian']['input'],
                                  output=statement['result']['russian']['output'],
                                  notes=statement['result']['russian']['notes'],
                                  name=statement['result']['russian']['name'], time_limit=info['result']['timeLimit'],
                                  memory_limit=info['result']['memoryLimit'],
                                  input_file=info['result']['inputFile'], output_file=info['result']['outputFile'])
    # if Statement.objects.filter(name=instance.statement.name):
        # Statement.objects.get(name=instance.statement.name).delete()
    cur_statement.save()
    print('Done')
