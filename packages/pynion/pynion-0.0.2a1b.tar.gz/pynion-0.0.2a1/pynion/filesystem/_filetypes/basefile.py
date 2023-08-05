import os
import json
import pathlib

from ...          import Manager
from ...metaclass import Multiton
from ...errors.fe import FileOpenError                 as FOE
from ...errors.fe import FileWrongRequestedActionError as FWR

m = Manager()


class BaseFile(object):
    """
    The **BaseFile** :py:class:`pynion.Multiton` is a file management object
    created directly through the py:class:`pynion.File` factory.

    It specifically manages regular files.

    """
    __metaclass__ = Multiton

    _IDENTIFIER   = 'name'

    def __init__(self, file_name, action):
        self.fname    = pathlib.Path(file_name)
        self.action   = action
        self._fd      = None
        self._pattern = None

    ##############
    # ATTRIBUTES #
    ##############
    @property
    def full(self):
        """
        :return: Full path of the file
        :rtype: str
        """
        try:
            return str(self.fname.resolve())
        except:
            return os.path.abspath(str(self.fname))

    @property
    def dir(self):
        """
        :return: Full path containing directory
        :rtype: str
        """
        return str(self.fname.resolve().parent)

    @property
    def last_dir(self):
        """
        :return: Name of the containing directory
        :rtype: str
        """
        return str(self.fname.resolve().parent.name)

    @property
    def name(self):
        """
        :return: Name of the file
        :rtype: str
        """
        return str(self.fname.name)

    @property
    def prefix(self):
        """
        :return: Name of the file without extension
        :rtype: str
        """
        return str(self.fname.stem)

    @property
    def first_prefix(self):
        """
        :return: Name of the first section of the file
        :rtype: str
        """
        return self.name.split('.')[0]

    @property
    def extension(self):
        """
        :return: Name of the file's extension
        :rtype: str
        """
        return str(self.fname.suffix)

    @property
    def extensions(self):
        """
        :return: List of all the sections of the file name except the first one.
        :rtype: list
        """
        return self.fname.suffixes

    @property
    def descriptor(self):
        """
        :return: Descriptor of the stored file
        :rtype: str
        """
        return self._fd

    @property
    def size(self):
        """
        :return: File size
        :rtype: str
        """
        return self.name.stat().st_size

    @property
    def pattern(self):
        """
        :return: Dictionary with the pattern assigned sections of the file name.
        :rtype: dict
        """
        if self._pattern is None:
            return None
        pattern = {}
        for p in self._pattern:
            pattern[p] = self.__dict__[p]
        return pattern

    ############
    # BOOLEANS #
    ############
    @property
    def is_open(self):
        """
        :return: Check if the file descriptor is open
        :rtype: bool
        """
        return self._fd is not None

    @property
    def is_to_write(self):
        """
        :return: Check if the file is set to write
        :rtype: bool
        """
        return self.action in set(['w', 'a'])

    @property
    def is_to_read(self):
        """
        :return: Check if the file is set to read
        :rtype: bool
        """
        return self.action in set(['r'])

    ###########
    # METHODS #
    ###########
    def relative_to(self, path = pathlib.Path.cwd()):
        """
        :param str path: Path to which the relative path is required.

        :return: Actual path relative to the query path
        :rtype: str
        """
        return self.fname.relative_to(path)

    ####################
    # METHODS: ON FILE #
    ####################
    def open(self):
        """
        Open the file in the previously defined action type.
        :rtype: self
        """
        if self.is_open:
            return self
        self._fd = open(self.full, self.action)
        return self

    def read(self):
        """
        :raise: :py:class:`pynion.errors.fe.FileWrongRequestedActionError` if
            opened in write mode.
        :rtype: File Descriptor
        """
        self._check_action('r')
        return self._fd

    def readline(self):
        """
        :raise: :py:class:`pynion.errors.fe.FileWrongRequestedActionError` if
            opened in write mode.
        :return: One line of the file.
        :rtype: str
        """
        self._check_action('r')
        return self._fd.readline()

    def readJSON(self, encoding = 'utf-8'):
        """
        Retrieve all data in file as a JSON dictionary.

        :raise: :py:class:`pynion.errors.fe.FileWrongRequestedActionError` if
            opened in write mode.
        :rtype: dict
        """
        d = []
        self.open()
        for l in self.read():
            d.append(l.strip())
        return json.loads(''.join(d), encoding=encoding)

    def write(self, line):
        """
        Write to the file

        :raise: :py:class:`pynion.errors.fe.FileWrongRequestedActionError` if
            opened in read mode.
        """
        self._check_action('w')
        self._fd.write(line)

    def flush(self):
        """
        :raise: :py:class:`pynion.errors.fe.FileWrongRequestedActionError` if
            opened in read mode.
        """
        self._check_action('w')
        self._fd.flush()

    def close(self):
        """
        Close the file.
        """
        self._fd.close()
        self._fd = None

    ###################
    # PRIVATE METHODS #
    ###################
    def _check_action(self, call_method):
        if not self.is_open:
            raise FOE(self.full, self.action)
        if call_method == 'r' and self.is_to_write:
            raise FWR(self.full, self.action)
        elif call_method == 'w' and self.is_to_read:
            raise FWR(self.full, self.action)

    #################
    # MAGIC METHODS #
    #################
    def __str__(self):
        return self.full

    def __repr__(self):
        cls = '.'.join([self.__class__.split('.')[0],
                        self.__class__.split('.')[-1]])
        return '<{0}: {1.full}>'.format(cls, self)
