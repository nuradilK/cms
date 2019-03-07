import os
import shutil
import subprocess

from os.path import join as path_join
from os.path import normpath


class Sandbox:
    ISOLATE_DIR = path_join('.', 'isolate')
    BOXES_DIR = 'boxes'

    def run_cmd(self, cmd, with_code=False):
        cmd_list = cmd.split()
        p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.get_box_dir())
        out, err = p.communicate()
        if with_code:
            return out, err, p.returncode
        return out, err

    def run_isolate(self, cmd_list):
        p = subprocess.Popen(['sudo', path_join(self.ISOLATE_DIR, 'isolate')] + cmd_list,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return out, err

    def init(self, box_id=0):
        """ Initialize sandbox """

        self.box_id = box_id

        out, err = self.run_isolate(['--init', '--box-id', str(box_id)])

        if err != b'':
            self.cleanup()
            self.box_id = box_id
            self.run_isolate(['--init', '--box-id', str(box_id)])

        os.makedirs(path_join(os.getcwd(), self.get_box_dir(), 'box'))

    def cleanup(self):
        """ Cleanup sandbox """
        if self.box_id is None:
            return

        # When called from __del__, running subprocess can cause troubles
        # self.run_isolate(['--cleanup', '--box-id', str(self.box_id)])
        os.system('sudo ' + path_join(self.ISOLATE_DIR, 'isolate') + ' --cleanup --box-id ' + str(self.box_id))

        shutil.rmtree(path_join(self.BOXES_DIR, str(self.box_id)))

        self.box_id = None

    def __del__(self):
        if self.box_id is None:
            return
        self.cleanup()

    def get_box_dir(self, path=''):
        return normpath(path_join('.', self.BOXES_DIR, str(self.box_id), path))

    def get_box_path(self, path=''):
        return normpath(path_join(os.getcwd(), self.BOXES_DIR, str(self.box_id), path))

    def create_files(self, file_list):
        """ Adding files to sandbox

            file_list - list of tuples (name, content, file_dir):
        """

        for name, content, file_dir in file_list:
            self.create_file(name, content, file_dir)

    def create_file(self, name, content, file_dir='', is_public=True):
        """ Adding file to sandbox

            name - File name
            content - File content
            file_dir - File location
        """

        box_path = normpath(path_join(os.getcwd(), self.get_box_dir()))
        file_dir_path = normpath(path_join(box_path, file_dir))

        if not os.path.exists(file_dir_path):
            os.makedirs(file_dir_path)

        f_mode = 'w'
        if is_public:
            f_mode += '+'
        with open(path_join(file_dir_path, name), f_mode) as file:
            file.write(content)

        if is_public:
            os.chmod(path_join(file_dir_path, name), 0o777)

    def get_file(self, name):
        """
        :param name: File name
        :return: file content
        """
        with open(self.get_box_dir(name), 'r') as f:
            content = f.read()

        return content

    def run_exec(self, exec, cmd='', time_limit=1000, memory_limit=256, extra_time=200,
            meta_file=None, stdin_file=None, stdout_file=None, stderr_file=None,
            chdir=None, dirs=[],
            max_processes=None, verbose=False, silent=False):
        """ Run executable file in sandbox with given command and limits

            main parameters:
            exec - executable to run
            cmd - command to run
            time_limit - time limit in ms
            memory_limit - memory limit in MB
            dirs[] - directory bindings
            stdin_file - file to read stdin from
            stdout_file - file to redirect stdout
            stderr_file - file to redirect stderr
        """

        time_limit = time_limit / 1000  # isolate wants time in seconds
        extra_time = extra_time / 1000
        memory_limit = memory_limit * 1000  # isolate wants memory in kilobytes

        cmd_list = []
        cmd_list += ['--mem=' + str(memory_limit)]
        cmd_list += ['--time=' + str(time_limit)]
        cmd_list += ['--wall-time=' + str(time_limit + time_limit + 1)]
        cmd_list += ['--extra-time=' + str(extra_time)]
        cmd_list += ['--box-id=' + str(self.box_id)]

        if meta_file is not None:
            cmd_list += ['--meta=' + meta_file]
        if stdin_file is not None:
            cmd_list += ['--stdin=' + stdin_file]
        if stdout_file is not None:
            cmd_list += ['--stdout=' + stdout_file]
        if stderr_file is not None:
            cmd_list += ['--stderr=' + stderr_file]

        if chdir is not None:
            cmd_list += ['--chdir=' + chdir]
        for in_dir, out_dir, options in dirs:
            dir_bind = '--dir=' + in_dir + '=' \
                       + path_join(os.getcwd(), self.BOXES_DIR, str(self.box_id), out_dir)
            if options is not None:
                dir_bind += ':' + options
            cmd_list += [dir_bind]

        if max_processes is not None:
            cmd_list += ['--processes=' + max_processes]

        if verbose is True:
            cmd_list += ['--verbose']
        if silent is True:
            cmd_list += ['--silent']

        cmd_list += ['--run']
        cmd_list += [exec]
        cmd_list += cmd.split()

        return self.run_isolate(cmd_list)

# TESTING:
# sandbox = Sandbox()
# sandbox.init()

# print(normpath(path_join(os.getcwd(), sandbox.get_box_dir())))
# input()

# sandbox.create_files([('main.cpp', """
# #include <iostream>

# using namespace std;

# int main() {

#     cout << "Successful run" << endl;

#     return 0;
# }

# """, ''), ('input.txt', 'rar kek', 'box'), ('output.txt', '', 'box')])
# input()

# out, err = sandbox.run_cmd('g++ -o ' + path_join('.', 'box', 'main') + ' ' + 'main.cpp')
# if err != b'':
#     print('Compilation Error:\n' + str(err))
#     exit(0)
# input()

# out, err = sandbox.run_exec("main", dirs=[('/box', 'box', 'rw')],
#                             meta_file=sandbox.get_box_dir('meta.txt'), stdin_file='input.txt',
#                             time_limit=1000, memory_limit=16)
# print(str(out) + '\n\n' + str(err))

# input()
