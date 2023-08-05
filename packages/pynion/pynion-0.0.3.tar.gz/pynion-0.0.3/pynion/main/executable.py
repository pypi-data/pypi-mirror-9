"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2013

@ [oliva's lab](http://sbi.imim.es)

"""

import os
import subprocess
import copy

from . import Manager
from ..errors.xe import ExecutableNoExistsError         as ENE
from ..errors.xe import ExecutableNotInPathError        as ENP
from ..errors.xe import ExecutablePermissionDeniedError as EPD

m = Manager()


class Executable(object):
    """
    Manages the execution of external programs.
    """
    def __init__(self, executable, path=None):
        """
        :param str executable: name of the executable program
        :param str path: path to the executable. Not needed if the executable
            is in the ``$PATH`` environment variable. Default is :py:data:`None`

        :raise: :py:class:`pynion.errors.xe.ExecutableNoExistsError` if the
            executable does not exist
        :raise: :py:class:`pynion.errors.xe.ExecutableNotInPathError` if the
            path is :py:data:`None` and the executable is not in the ``$PATH``
            environment variable.
        :raise: :py:class:`pynion.errors.xe.ExecutablePermissionDeniedrror` if
            executable has no execution permission
        """
        self._exec = executable
        self._path = path

        if path is not None:
            self._path = os.path.abspath(path)
        else:
            found = self._load_executable_path()
            if not found:
                raise ENP(self._exec)

        self._check_executable()

        self._command = []
        self._command.append(self.full_executable)

        self._backup_command = []

        m.detail('Executable for {0} created.'.format(self.full_executable))

    ##############
    # ATTRIBUTES #
    ##############
    @property
    def executable(self):
        """
        Name of the executable.

        :rtype: str
        """
        return self._exec

    @property
    def path(self):
        """
        Path to the executable.

        :rtype: str
        """
        return self._path

    @property
    def command(self):
        """
        Full command to execute.

        :rtype: list
        """
        return self._command

    @property
    def full_executable(self):
        """
        Full executable with path.

        :rtype: str
        """
        return os.path.join(self._path, self._exec)

    ###########
    # METHODS #
    ###########
    def add_attribute(self, attribute_value, attribute_id=None):
        """
        Adds a new parameter to the command.
        Specifically for parameters with 'tags' like '-i'.

        :param str attribute_value: value of the attribute to add
        :param str attribute_id: label of the attribute to add. By default is
            :py:data:`None`, which makes the function identical to
            :py:class:`pynion.Executable.add_parameter`.

        """
        if attribute_id is None:
            self.add_parameter(attribute_value)
        else:
            self._command.append(attribute_id)
            self._command.append(str(attribute_value))

    def add_parameter(self, parameter):
        """
        Adds a new stand alone parameter to the command.

        :param str parameter: value of the parameter to add

        """
        self._command.append(str(parameter))

    def clean_command(self):
        """
        Removes all attributes and parameters added to the command.
        """
        self._command = []
        self._command.append(self.full_executable)

    def backup_command(self):
        """
        Store a copy of the command up to that point to retrieve import
        afterwards.
        """
        self._backup_command = copy.deepcopy(self._command)

    def restore_command(self):
        """
        Retrieve the backup command into the working command.
        The backup command is emptied.
        """
        self._command        = self._backup_command
        self._backup_command = []

    def execute(self, silent=False):
        """
        Executes the commands.

        :param bool silent: If :py:data:`True`, external program STDERR is
            shown through STDERR

        :raises: :py:class:`SystemError` if an error occurs in the external program.
        """
        outPIPE = subprocess.PIPE if m._debug else open('/dev/null', 'w')
        errPIPE = open('/dev/null', 'w') if silent else subprocess.PIPE

        command = " ".join(self.command)
        m.info('\tExecuting:\t{0}'.format(command))

        try:
            p = subprocess.Popen(self.command, stdout = outPIPE,
                                               stderr = errPIPE)

            if m._debug:
                for out in iter(p.stdout.readline, b''):
                    m.info(out.strip())
            p.communicate()
        except:
            raise SystemError()

    ###################
    # PRIVATE METHODS #
    ###################
    def _load_executable_path(self):
        """
        Retrieves the executable path in case self._path is None.

        :return: :py:data:`True` if the path is found, :py:Data:`False` otherwise.
        :rtype: bool
        """
        search = ["which", self.executable]
        p = subprocess.Popen(search, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()

        if out != '':
            self._path = os.path.split(out.strip())[0]
            return True
        else:
            return False

    def _check_executable(self):
        if not os.path.isfile(self.full_executable):
            raise ENE(self.full_executable)
        if not os.access(self.full_executable, os.X_OK):
            raise EPD(self.full_executable)

    #################
    # CLASS METHODS #
    #################
    def __repr__(self):
        return " ".join(self._command)

    def __str__(self):
        return repr(self)
