from os.path import join as path_join

from celery import shared_task
from billiard import current_process

from .models import Submission, RunInfo
from sandbox.sandbox_manager import Sandbox


def get_meta(sandbox, meta_file):
    content = sandbox.get_file(meta_file).split('\n')
    content = list(line for line in content if line)

    meta = dict()
    for line in content:
        key, val = line.split(':')
        meta[key] = val

    return meta


def run_solution(sandbox, name, problem_info, test):
    sandbox.create_file(str(problem_info.input_file), str(test.input), file_dir='box')
    sandbox.create_file(str(problem_info.output_file), '', file_dir='box')
    sandbox.run_exec(name, dirs=[('/box', 'box', 'rw')], meta_file=sandbox.get_box_dir('meta'),
                     stdin_file=str(problem_info.input_file), stdout_file=str(problem_info.output_file),
                     time_limit=problem_info.time_limit, memory_limit=problem_info.memory_limit)


@shared_task
def evaluate_submission(sub_pk):
    """ Evaluate or re-evaluate submission """

    sub = Submission.objects.get(pk=sub_pk)
    sandbox = Sandbox()
    sandbox.init(current_process().index)

    sub.status = Submission.STATUS.COMPILING
    sub.save()

    # Compiling
    sandbox.create_file('main.cpp', str(sub.source), is_public=0)
    out, err = sandbox.run_cmd('g++ -o ' + path_join('box', 'main') + ' -std=c++11 -DONLINE_JUDGE main.cpp')
    if err != b'' or out != b'':
        sub.status = Submission.STATUS.COMPILATION_ERROR
        sub.save()
        return

    sub.status = Submission.STATUS.TESTING
    sub.save()

    # TODO properly access static files
    with open(path_join('.', 'submission', 'static', 'submission', 'testlib.h'), 'r') as testlib_file:
        testlib = testlib_file.read()

    sandbox.create_file('testlib.h', str(testlib), is_public=0)
    sandbox.create_file('check.cpp', str(sub.problem.checker), is_public=0)
    out, err = sandbox.run_cmd('g++ -o check -std=c++11 check.cpp testlib.h')
    if err != b'':
        print(err.decode('utf-8'))
        sub.status = Submission.STATUS.ERROR
        sub.save()
        return

    problem_info = sub.problem.statement
    if not sub.is_invocation:
        participant = sub.participant
        if participant.submission_set.filter(problem=sub.problem).order_by('-points'):
            participant.score -= participant.submission_set.filter(problem=sub.problem).order_by(
                '-points').first().points
    for subtask in sub.problem.subtask_set.order_by('subtask_id'):
        cur_score = subtask.score
        for test in subtask.test_set.order_by('test_id'):
            sub.current_test = test.test_id
            sub.save()

            run_solution(sandbox, 'main', problem_info, test)

            meta = get_meta(sandbox, 'meta')

            run_info = sub.runinfo_set.filter(test=test)
            if run_info:
                run_info = run_info.first()
            else:
                run_info = sub.runinfo_set.create(test=test)

            if 'status' not in meta:
                if sub.is_invocation:
                    run_info.status = RunInfo.STATUS.OK
                    run_info.time = float(meta['time'])
                    test.output = sandbox.get_file(path_join('box', problem_info.output_file))
                    test.save()
                else:
                    ans_file = 'test.a'
                    sandbox.create_file(ans_file, str(test.output), is_public=0)
                    out, err, code = sandbox.run_cmd('./check ' +
                                                     path_join('.', 'box', str(problem_info.input_file)) + ' ' +
                                                     path_join('.', 'box', str(problem_info.output_file)) + ' ' +
                                                     path_join('.', ans_file), with_code=True)
                    if code == 0:
                        run_info.status = RunInfo.STATUS.OK
                    elif code == 1:
                        run_info.status = RunInfo.STATUS.WA
                    elif code == 2:
                        run_info.status = RunInfo.STATUS.PE
                    elif code == 3:
                        run_info.status = RunInfo.STATUS.CF
                    run_info.time = float(meta['time'])
            elif meta['status'] == 'TO':
                if meta['message'] == 'Time limit exceeded':
                    run_info.status = RunInfo.STATUS.TL
                else:
                    run_info.status = RunInfo.STATUS.WTL
                run_info.time = float(problem_info.time_limit)
            elif meta['status'] == 'SG' or meta['status'] == 'RE':
                run_info.status = RunInfo.STATUS.RE
                run_info.time = float(meta['time'])
            else:
                run_info.status = RunInfo.STATUS.XX
            if run_info.status != RunInfo.STATUS.OK:
                cur_score = 0
            run_info.save()
        sub.points += cur_score
        sub.save()
    sub.status = Submission.STATUS.FINISHED
    sub.save()
    if not sub.is_invocation:
        participant.score = participant.submission_set.filter(problem=sub.problem).order_by('-points').first().points
        participant.save()
    sandbox.cleanup()
