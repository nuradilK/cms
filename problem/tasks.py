import requests
import time
import hashlib
import string
import random

from os.path import join as path_join
from celery import shared_task
from billiard import current_process
from sandbox.sandbox_manager import Sandbox

from .models import Statement, Test, Problem, Subtask
from .std_checkers import codes

from submission.models import Submission, RunInfo
from submission.tasks import evaluate_submission

api_url = "https://polygon.codeforces.com/api/"


def param_config(params):
    for key in list(params.keys()):
        if key not in ['apiKey', 'apiSig', 'time', 'problemId']:
            params.pop(key, None)


def gen_hash():
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=6))


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


def get_statement(params, instance, current_time):
    param_config(params)
    method = 'problem.statements'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('problemId', str(instance.problem_id)),
                 ('time', current_time)]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    return requests.get(api_url + method, params).json()['result']


def get_info(params, instance, current_time):
    param_config(params)
    method = 'problem.info'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('problemId', str(instance.problem_id)),
                 ('time', current_time)]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    return requests.get(api_url + method, params).json()['result']


def get_test(params, instance, current_time):
    param_config(params)
    method = 'problem.tests'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('problemId', str(instance.problem_id)),
                 ('testset', instance.testset_name), ('time', current_time)]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    params['testset'] = instance.testset_name
    return requests.get(api_url + method, params).json()


def get_name(params, instance, current_time):
    param_config(params)
    method = 'problem.checker'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('problemId', str(instance.problem_id)),
                 ('time', current_time)]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    return requests.get(api_url + method, params).json()['result']


def get_file(params, instance, current_time, name):
    param_config(params)
    method = 'problem.viewFile'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('name', name), ('problemId', str(instance.problem_id)),
                 ('time', current_time), ('type', 'source')]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    params['name'] = name
    params['type'] = 'source'
    return requests.get(api_url + method, params).content.decode('utf-8')


def get_files_list(params, instance, current_time):
    param_config(params)
    method = 'problem.files'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('problemId', str(instance.problem_id)),
                 ('time', current_time)]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    return requests.get(api_url + method, params).json()


def get_solution_name(params, instance, current_time):
    param_config(params)
    method = 'problem.solutions'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('problemId', str(instance.problem_id)),
                 ('time', current_time)]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)

    solution_list = requests.get(api_url + method, params).json()['result']
    main_solution = None
    correct_solution = None
    for solution in solution_list:
        if solution['tag'] == 'MA':
            main_solution = solution
        if solution['tag'] == 'OK':
            correct_solution = solution

    if main_solution is None:
        return correct_solution['name']
    return main_solution['name']


def get_solution_source(params, instance, current_time, solution_name):
    param_config(params)
    method = 'problem.viewSolution'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('name', solution_name), ('problemId', str(instance.problem_id)),
                 ('time', current_time)]
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    params['name'] = solution_name

    return requests.get(api_url + method, params).content.decode('utf-8')


def generator_code(params, instance, current_time, script_line):
    param_config(params)
    name = script_line.split()[0] + '.cpp'
    method = 'problem.viewFile'
    my_params = [('apiKey', str(instance.polygon_account.key)), ('name', name), ('problemId', str(instance.problem_id)),
                 ('time', current_time), ('type', 'source')]
    params['type'] = 'source'
    params['name'] = name
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, my_params)
    gen_code = requests.get(api_url + method, params).text
    return gen_code


def manual_test(instance, test, fullSubtask):
    instance.test_set.create(input=test['input'], test_id=test['index'], in_statement=test['useInStatements'], subtask=fullSubtask)


def script_test(instance, script_line, gen_source, gen_name, test, fullSubtask):
    sandbox = Sandbox()
    sandbox.init(current_process().index)

    # CREATE FILES
    with open(path_join('.', 'problem', 'static', 'problem', 'testlib.h'), 'r') as testlib_file:
        testlib = testlib_file.read()
    sandbox.create_file(gen_name + '.cpp', str(gen_source), is_public=0)
    sandbox.create_file('testlib.h', str(testlib), is_public=0)

    # COMPILE
    sandbox.run_cmd(
        'g++ -o ' + path_join('box', gen_name) + ' -std=c++11 -DONLINE_JUDGE ' + gen_name + '.cpp ' + 'testlib.h')

    # GET TEST
    out, err = sandbox.run_exec(exec=gen_name, cmd=' '.join(script_line.split()[1:]), dirs=[('/box', 'box', 'rw')],
                                meta_file=sandbox.get_box_dir('meta'),
                                time_limit=10, memory_limit=128)

    instance.test_set.create(input=out.decode('utf-8'), test_id=test['index'], in_statement=test['useInStatements'], subtask=fullSubtask)
    sandbox.cleanup()


def create_tests(instance, params, current_time, tests, fullSubtask):
    for test in tests['result']:
        if test['manual'] is True:
            manual_test(instance, test, fullSubtask)
        else:
            script_test(instance, test['scriptLine'],
                        generator_code(params, instance, current_time, test['scriptLine']),
                        test['scriptLine'].split()[0], test, fullSubtask)


@shared_task
def process_problem(prob_pk):
    instance = None
    # TODO Resolve 'Problem.DoesNotExist' issue
    while instance is None:
        try:
            instance = Problem.objects.get(pk=prob_pk)
        except Problem.DoesNotExist:
            pass

    Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.IN_PROCESS)

    if hasattr(instance, 'statement'):
        instance.statement.delete()
    if hasattr(instance, 'test_set'):
        instance.test_set.all().delete()

    current_time = str(int(time.time()))
    params = {
        'apiKey': instance.polygon_account.key,
        'time': current_time,
        'problemId': instance.problem_id,
    }
    fullSubtask = Subtask(problem=Problem.objects.get(pk=instance.pk), description='Full Subtask')
    fullSubtask.save()
    try:
        statement = get_statement(params, instance, current_time)
        info = get_info(params, instance, current_time)
        checker_name = get_name(params, instance, current_time)
        solution_name = get_solution_name(params, instance, current_time)
        solution = get_solution_source(params, instance, current_time, solution_name)
        tests = get_test(params, instance, current_time)
    except Exception as e:
        print(e)
        Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.FAILED)
        return

    have = False
    for key in codes:
        if key == checker_name:
            have = True

    # TODO Fix for the case when custom checker has the same name as a standard one
    if not have:
        try:
            checker = get_file(params, instance, current_time, checker_name)
        except Exception as e:
            print(e)
            Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.FAILED)
            return
    else:
        checker = codes[checker_name]

    instance.checker = checker
    Problem.objects.filter(pk=instance.pk).update(checker=checker)

    instance.solution = solution
    Problem.objects.filter(pk=instance.pk).update(solution=solution)

    lang = 'english' if 'english' in statement else 'russian'
    if lang in statement:
        cur_statement = Statement(problem=instance, legend=statement[lang]['legend'],
                                  input=statement[lang]['input'],
                                  output=statement[lang]['output'],
                                  notes=statement[lang]['notes'],
                                  name=statement[lang]['name'], time_limit=info['timeLimit'],
                                  memory_limit=info['memoryLimit'],
                                  input_file=info['inputFile'], output_file=info['outputFile'])
    else:
        cur_statement = Statement(problem=instance)
    cur_statement.save()

    create_tests(instance, params, current_time, tests, fullSubtask)

    invocation = instance.submission_set.create(source=solution, is_invocation=True)
    Problem.objects.filter(pk=instance.pk).update(invocation_pk=invocation.pk)
    evaluate_submission(invocation.pk)
    invocation.refresh_from_db()

    if invocation.status != Submission.STATUS.FINISHED or invocation.runinfo_set.exclude(status=RunInfo.STATUS.OK):
        Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.FAILED)
        return

    Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.READY)
