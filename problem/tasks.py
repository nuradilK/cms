import requests
import time
import hashlib
import string
import random
import traceback

from os.path import join as path_join
from celery import shared_task
from billiard import current_process
from sandbox.sandbox_manager import Sandbox

from .models import Statement, Test, Problem, Subtask
from .std_checkers import sources as std_checkers

from submission.models import Submission, RunInfo
from submission.tasks import evaluate_submission

api_url = "https://polygon.codeforces.com/api/"


def gen_hash():
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=6))


def api_sig(method, secret, add):
    api_hash = gen_hash()
    signature = api_hash + '/' + method
    started = False
    for key in sorted(add):
        value = add[key]
        if started is False:
            signature = signature + '?'
        else:
            signature = signature + '&'
        signature = signature + key + '=' + value
        started = True
    signature = signature + '#' + secret
    return api_hash + hashlib.sha512(str(signature).encode('utf-8')).hexdigest()


def problem_api_request(method, instance, extra_params=None, is_source_file=False):
    method = 'problem.' + method
    current_time = str(int(time.time()))
    extra_params = extra_params or {}
    params = {
        'apiKey': instance.polygon_account.key,
        'time': current_time,
        'problemId': instance.problem_id,
    }
    params = {**params, **extra_params}
    params['apiSig'] = api_sig(method, instance.polygon_account.secret, params)

    resp = requests.get(api_url + method, params)

    if resp.status_code != 200:
        raise Exception('API request error. Polygon can be unavailable.')

    if not is_source_file:
        result = resp.json()
        if result['status'] == 'FAILED':
            raise Exception(result['comment'])
        result = result['result']
    else:
        result = resp.content.decode('utf-8')

    return result


def get_solution_name(instance):
    solution_list = problem_api_request('solutions', instance)
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


def manual_test(instance, test, full_subtask):
    instance.test_set.create(input=test['input'], test_id=test['index'], in_statement=test['useInStatements'],
                             subtask=full_subtask)


def script_test(instance, script_line, gen_source, gen_name, test, full_subtask):
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

    instance.test_set.create(input=out.decode('utf-8'), test_id=test['index'], in_statement=test['useInStatements'],
                             subtask=full_subtask)
    sandbox.cleanup()


def create_tests(instance, tests, full_subtask):
    for test in tests:
        if test['manual'] is True:
            manual_test(instance, test, full_subtask)
        else:
            try:
                generator_source = problem_api_request('viewFile', instance, is_source_file=True, extra_params={
                    'name': test['scriptLine'].split()[0] + '.cpp',
                    'type': 'source',
                })
            except Exception as e:
                fail_problem_processing(instance, e=e, message='Error loading generator for test ' + str(test.test_id))
                return
            script_test(instance, test['scriptLine'], generator_source,
                        test['scriptLine'].split()[0], test, full_subtask)


def get_checker_source(instance):
    checker_name = problem_api_request('checker', instance)
    checker_source = None
    for name, source in std_checkers.items():
        if name == checker_name:
            checker_source = source

    if checker_source is None:
        checker_source = problem_api_request('viewFile', instance, is_source_file=True, extra_params={
            'name': checker_name,
            'type': 'source',
        })

    return checker_source


def fail_problem_processing(instance, e=None, message=None):
    if message:
        print(str(message))
    if e:
        print(traceback.format_exc())
    Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.FAILED)


def clear_problem(instance):
    if hasattr(instance, 'statement'):
        instance.statement.delete()
    if hasattr(instance, 'test_set'):
        instance.test_set.all().delete()
    if hasattr(instance, 'subtask_set'):
        instance.subtask_set.all().delete()
    instance.checker = ''
    instance.solution = ''
    instance.invocation_pk = ''

    Problem.objects.filter(pk=instance.pk).update(checker='', solution='', invocation_pk='')
    return instance


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

    instance = clear_problem(instance)

    # Loading data from Polygon
    try:
        statement = problem_api_request('statements', instance)
        info = problem_api_request('info', instance)
        checker = get_checker_source(instance)
        solution_name = get_solution_name(instance)
        solution = problem_api_request('viewSolution', instance, is_source_file=True,
                                       extra_params={'name': solution_name})
        tests = problem_api_request('tests', instance, extra_params={'testset': instance.testset_name})
    except Exception as e:
        fail_problem_processing(instance, e=e, message='Error loading problem data')
        return

    # Processing data
    lang = 'english' if 'english' in statement else 'russian'
    if lang in statement:
        statement = statement[lang]
        Statement.objects.create(problem=instance, legend=statement['legend'],
                                 input=statement['input'],
                                 output=statement['output'],
                                 notes=statement['notes'],
                                 name=statement['name'], time_limit=info['timeLimit'],
                                 memory_limit=info['memoryLimit'],
                                 input_file=info['inputFile'], output_file=info['outputFile'])
    else:
        Statement.objects.create(problem=instance)

    Problem.objects.filter(pk=instance.pk).update(checker=checker)
    Problem.objects.filter(pk=instance.pk).update(solution=solution)

    full_subtask = Subtask(problem=Problem.objects.get(pk=instance.pk), description='Full Subtask')
    full_subtask.save()

    create_tests(instance, tests, full_subtask)

    # Generating output for tests
    invocation = instance.submission_set.create(source=solution, is_invocation=True)
    Problem.objects.filter(pk=instance.pk).update(invocation_pk=invocation.pk)
    evaluate_submission(invocation.pk)
    invocation.refresh_from_db()

    if invocation.status != Submission.STATUS.FINISHED or invocation.runinfo_set.exclude(status=RunInfo.STATUS.OK):
        Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.FAILED)
        return

    Problem.objects.filter(pk=instance.pk).update(status=Problem.STATUS.READY)
