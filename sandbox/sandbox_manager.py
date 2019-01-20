import os
import subprocess

def run_isolate(cmd):
    path_to_isolate = os.path.join('..', 'isolate', 'isolate')
    cmd_list = cmd.split()

    p = subprocess.Popen([path_to_isolate] + cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.communicate()

class Sandbox:

    def __init__(self):
        """ Initialize isolate sandbox """

        self.box_id = -1
        out = b''
        err = b''
        while out == b'':
            self.box_id += 1
            out, err = run_isolate("--init -b " + str(self.box_id))

    def cleanup(self):
        """ Cleanup isolate sandbox """

        run_isolate("--cleanup -b " + str(self.box_id))


sandbox = Sandbox()
sandbox.cleanup()