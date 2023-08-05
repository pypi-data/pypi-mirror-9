"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
import atexit
import ConfigParser
import datetime
import inspect
import json
import logging
import os
import sys
import time
import traceback
import warnings

from ..metaclass  import Singleton
from ._inner      import Project
from ._inner      import Experiment


class Manager(object):
    """The Manager class is a :py:class:`Singleton <pynion.Singleton>` that crosses
    through the entire library. It is the main controller of the user's preferences.

    """
    __metaclass__ = Singleton

    _GENERAL_FORMAT = '%(asctime)s - %(levelname)-7.7s - %(message)s'
    _TIME_FORMAT    = '%Y-%m-%d %H:%M'
    _FRMT           = logging.Formatter(_GENERAL_FORMAT, _TIME_FORMAT)
    _MSSG           = '[ {0} ] - {1}'

    def __init__(self):
        """.. py:method:: __init__()

        The class is instantiated at some point during the load of the library's
        code. Thus, no parameters are passed to it. As any new instantiation will
        only call the initial instance, parameters cannot be passed afterward.

        Although any attribute can be accessed through its given *setter*, default
        values can be assigned to the first initialization of **Manager** through
        a configuration file. The configuration file should have the following
        parameters:

        .. literalinclude:: /../../pynion/config/default.settings

        The user's configuration file must then be linked to a system variable
        named ``PYNION_CONFIG_PY``. Thus, the configuration file can be setted
        globally for all executions directly from bash, ::

            export PYNION_CONFIG_PY=user.settings

        Or specifically to a script by ::

            import os
            os.environ["PYNION_CONFIG_PY"] = 'user.settings'

        **BEFORE** importing the **Pynion** library.

        Regarding the different execution parameters in the configuration file:

        :param bool stdout: Create a :py:class:`logging.StreamHandler` for standard
            output.
        :param bool verbose: Activate level *verbose* of logging report.
        :param bool debug: Activate level *debug* of logging report. It also
            forces the activation of *verbose*.
        :param bool detail: Activate level *detail* of logging report. It also
            forces the activation of *debug*, *verbose* and *unclean*.
        :param bool overwrite: When :py:data:`True`, allows overwriting existing files.
        :param bool unclean: When :py:data:`True`, avoids the deletion of
            temporary and empty files at the end of the execution.
        :param bool logfile: When defined, it creates a
            :py:class:`logging.StreamHandler` to a file with the provided name.
            If ``logfile = default`` or a directory, it creates a logfile with
            a predefined name that includes the name of the execution and the
            pid of the process.

        Regarding the project parameters in the configuration file:
        **(TODO)**

        """
        # Logger parameters: Level of detail
        self._verbose = False  # Requires setter
        self._debug   = False  # Requires setter
        self._detail  = False  # Requires setter

        # Management parameters:
        self._tempfiles = set()  # Requires setter
        self._clean     = True   # Clean the temporary files

        # IO conditions:
        self._overwrite = False  # Requires setter

        # Create a logger.
        # Null handler is added so that if no handler is active
        # warnings and errors will not display a 'handler not found' message
        self._stdout = False
        self._fd = logging.getLogger(__name__)
        self._fd.setLevel(logging.DEBUG)
        self._fd.addHandler(logging.NullHandler())

        # Project and Experiment
        rfname, cfname, pfname = self._configuration()
        self.project = Project(rfname, cfname, pfname)
        try:
            self.experiment = Experiment()
        except:
            self.exception(['Bash command could not be imported.',
                            'System needs to be UNIX based'])

        # Citation Manager
        self.citations = set()

        # Register function to execute at exit
        atexit.register(self.shutdown)
        atexit.register(self.cleanup)

    ####################
    # METHODS: SETTERS #
    ####################
    def set_verbose(self):
        """Activate level *verbose* of logging report"""
        self._verbose = True

    def set_debug(self):
        """Activate level *debug* of logging report. It also forces the
        activation of *verbose*."""
        self.set_verbose()
        self._debug  = True

    def set_detail(self):
        """Activate level *detail* of logging report. It also forces the
        activation of *debug*, *verbose* and *unclean*."""
        self._detail = True
        self.set_unclean()
        self.set_debug()

    def set_unclean(self):
        """Avoids the deletion of temporary and empty
        files at the end of the execution."""
        self._clean = False

    def set_stdout(self):
        """Create a :py:class:`logging.StreamHandler` for standard output."""
        if self._stdout: return
        handler = logging.StreamHandler()
        handler.setFormatter(self._FRMT)
        self._fd.addHandler(handler)
        self.info('Active STDOUT')
        self._stdout = True

    def set_overwrite(self):
        """Allows overwriting existing files."""
        self._overwrite = True

    def set_logfile(self, logname = os.getcwd()):
        """Creates a :py:class:`logging.StreamHandler` to a file.

        :param str logname: Name of the output logging file. If logname is a
            directory, it will create a logging file in that directory named by
            the name of the execution and its pid. Default value is current
            working directory.
        """
        if os.path.isdir(logname):
            script_name = os.path.split(os.path.splitext(sys.argv[0])[0])[1]
            if script_name == '__main__':
                script_name = os.path.split(os.path.split(sys.argv[0])[0])[1]
            log_file    = ".".join([script_name, str(os.getpid()), 'log'])
            logname     = os.path.join(logname, log_file)

        self.info('LOGfile: {0}'.format(logname))
        handler = logging.FileHandler(filename = logname)
        handler.setFormatter(self._FRMT)
        self._fd.addHandler(handler)

    ###########
    # METHODS #
    ###########
    def add_temporary_file(self, tempfile):
        """Register a new temporary file.

        :param str tempfile: Name of the temporary file.
        """
        self.info('Registering temporary file {0}'.format(tempfile))
        self._tempfiles.add(tempfile)

    def add_experiment_file(self, filename, action):
        """Register a new experiment file.

        :param str filename: Name of the experiment file.
        :param str action: Open mode of the registered file ('r', 'w', 'a')
        """
        self.experiment.add_file(filename, action)

    def add_citation(self, citation):
        """Adds a new citation from some code or other to be printed at the
            end of the execution.

        :param str citation: Citation to strore
        """
        self.citations.add(citation)

    def countdown(self, max_time):
        """Generate a STDERR printed countdown when needed to wait for something.

        :param int max_time: Time to wait, in seconds.
        """
        t  = str(datetime.timedelta(seconds=max_time))
        n  = time.localtime()
        s1 = 'Waiting for: {0} hours'.format(t)
        s2 = 'Wait started at {0}'.format(time.strftime('%X', n))
        s3 = 'on {0}'.format(time.strftime('%Y-%m-%d', n))
        sys.stderr.write('{0}\t{1} {2}\n\n'.format(s1, s2, s3))
        while max_time > 0:
            t = str(datetime.timedelta(seconds=max_time))
            sys.stderr.write('Remaining: {0} hours'.format(t))
            time.sleep(1)
            max_time -= 1
            if bool(max_time):
                sys.stderr.write('\r')
            else:
                sys.stderr.write('\r')
                t = str(datetime.timedelta(seconds=max_time))
                sys.stderr.write('Remaining: {0} hours'.format(t))
                sys.stderr.write('\n')

    def evaluate_overwrite(self, overwrite):
        """Given a overwrite command, it evaluates it with the global
        overwrite configuration.

        :param bool overwrite: Particular overwrite status.
        :return: Final overwrite status
        :rtype: bool
        """
        return self._overwrite if overwrite is None else overwrite

    ####################
    # METHODS: LOGGING #
    ####################
    def info(self, mssg):
        """Print *verbose* level information.

        :param str mssg: Message to relay through logging. If it is :py:data:`list`,
            each position is treated as a new line.
        """
        if not self._verbose:
            return
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            self._fd.info(line)

    def debug(self, mssg):
        """Print *debug* level information.

        :param str mssg: Message to relay through logging. If it is :py:data:`list`,
            each position is treated as a new line.
        """
        if not self._debug:
            return
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            self._fd.debug(line)

    def detail(self, mssg):
        """Print *detail* level information.

        :param str mssg: Message to relay through logging. If it is :py:data:`list`,
            each position is treated as a new line.
        """
        if not self._detail:
            return
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            self._fd.debug(line)

    def warning(self, mssg):
        """Print *warning*.

        :param str mssg: Message to relay through logging. If it is :py:data:`list`,
            each position is treated as a new line.
        """
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            # If we have no handler added, we warn through the warnings module
            if len(self._fd.handlers) > 1:
                self._fd.warning(line)
            else:
                warnings.warn(line + '\n')

    def exception(self, mssg):
        """Print *exceptions* and quit.

        :param str mssg: Message to relay through logging. If it is :py:data:`list`,
            each position is treated as a new line.
        """
        callerID = self._caller(inspect.stack()[1][0])
        for line in self._message_to_array(callerID, mssg):
            if len(self._fd.handlers) > 1:
                self._fd.exception(line)
            else:
                sys.stderr.write(line + '\n')
                traceback.print_tb(sys.exc_info()[2])
        os._exit(0)  # This exit avoids atexit calls.

    ####################
    # METHODS: AT EXIT #
    ####################
    def cleanup(self):
        if self._clean:
            for tfile in self._tempfiles:
                if os.path.isfile(tfile):
                    os.unlink(tfile)
                    self.info('Temporary file {0} removed.'.format(tfile))
            for efile in self.experiment.clean_empty_files():
                self.info('Empty file {0} removed.'.format(efile))
        self._tempfiles = set()

    def shutdown(self):
        self.experiment.end = time.time()
        self.experiment.calculate_duration()

        self._write_to_pipeline()

        info = 'Elapsed time: {0}'.format(self.experiment.duration)
        if not self._verbose: self.set_verbose()
        if not self._stdout:  self.set_stdout()
        for _ in self.citations:
            self._fd.info('[ REFERENCE!! ]: -- {0}'.format(_))
        self._fd.info('[ SUCCESS!! ]: -- {0}'.format(info))
        self._fd.info('[ SUCCESS!! ]: -- Program ended as expected.')

        logging.shutdown()

    ###################
    # PRIVATE METHODS #
    ###################
    def _caller(self, caller):
        if inspect.getmodule(caller) is not None:
            callerID = inspect.getmodule(caller).__name__
        else:
            callerID = 'Terminal'

        if callerID is '__main__':
            callerID = inspect.getmodule(caller).__file__
            callerID = os.path.split(os.path.split(callerID)[0])[-1]
        return callerID.upper()

    def _message_to_array(self, callerID, mssg):
        if isinstance(mssg, basestring):
            mssg = [mssg, ]
        for line in mssg:
            yield self._MSSG.format(callerID, str(line))

    def _write_to_pipeline(self):
        if self.project.is_active:
            data = []
            with open(self.project.pipeline_file, 'r') as line:
                l = line.read().strip()
                if len(l) > 0:
                    data = json.loads(l)
            data.append(self.experiment.to_dict())
            with open(self.project.pipeline_file, 'w') as fd:
                fd.write(json.dumps(data))

    def _configuration(self):
        dfile   = '../config/default.settings'
        ufile   = '../config/user.settings'
        default = os.path.join(os.path.dirname(__file__), dfile)
        default = os.path.normpath(default)
        user    = os.path.join(os.path.dirname(__file__), ufile)
        user    = os.path.normpath(user)
        user    = os.getenv('PYNION_CONFIG_PY', user)

        parse  = ConfigParser.RawConfigParser(allow_no_value=True)
        parse.readfp(open(default))
        parse.read(user)

        manager_opt = ['stdout',    'verbose',
                       'debug',     'detail',
                       'overwrite', 'unclean']

        for opt in manager_opt:
            func = getattr(self, 'set_' + opt)
            if parse.getboolean('manager', opt):
                self.info('Setting up {0} mode'.format(opt))
                func()
        logfile = parse.get('manager', 'logfile')
        if logfile is not None and logfile != '':
            if logfile.lower() == 'default':
                self.set_logfile()
            else:
                self.set_logfile(logfile)

        return [parse.get('project', 'name'),
                parse.get('project', 'config'),
                parse.get('project', 'pipeline')]
