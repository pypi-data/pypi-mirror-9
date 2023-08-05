"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
# import collections
import datetime
import os
import platform
import pwd
import re
import socket
import subprocess
import sys
import time

from ...abstractclass import JSONer
from .  import Process


class Experiment(JSONer):

    def __init__(self):
        self.pyversion = platform.python_version()
        self.command   = sys.argv
        self.user      = pwd.getpwuid(os.getuid())[0]
        self.host      = socket.gethostname()
        self.system    = (platform.system(), platform.release())
        self.files     = {}
        self.start     = time.time()
        self.end       = None
        self.duration  = None

        self.process   = self._get_process()

    ###########
    # METHODS #
    ###########
    def add_file(self, file_name, action):
        self.files.setdefault(action, []).append(file_name)

    ####################
    # METHODS: AT EXIT #
    ####################
    def calculate_duration(self):
        self.duration = self.end - self.start
        self.duration = str(datetime.timedelta(seconds=self.duration))

    def clean_empty_files(self):
        if 'w' in self.files:
            for efile in self.files['w']:
                if os.path.isfile(efile) and os.path.getsize(efile) == 0:
                    os.unlink(efile)
                    yield efile

    ####################
    # METHODS: PRIVATE #
    ####################
    def _get_process(self):
        sub_proc = subprocess.Popen(['ps', 'aux'],
                                    shell=False, stdout=subprocess.PIPE)
        #Discard the first line (ps aux header)
        sub_proc.stdout.readline()
        pid = int(os.getpid())
        for line in sub_proc.stdout:
            #The separator for splitting is 'variable number of spaces'
            proc_info = re.split(" *", line.strip())
            p = Process(proc_info)
            if p.pid == pid:
                return p
