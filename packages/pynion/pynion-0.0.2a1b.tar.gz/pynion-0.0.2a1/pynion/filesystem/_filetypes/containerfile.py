import os
import tarfile
import zipfile

from .basefile    import BaseFile
from ...errors.fe import FileContainerFileNotFound     as CNF
from ...errors.fe import FileContainerFailedExtraction as CFE


class ContainerFile(BaseFile):
    """
    The **CompressedFile** :py:class:`pynion.Multiton` is a file management object
    created directly through the py:class:`pynion.File` factory.

    Extends :py:class:`pynion.filesystem._filetypes.BaseFile`

    It specifically manages compacted or compressed files with multiple files
    within.

    """

    def __init__(self, file_name, action, ctype):
        super(ContainerFile, self).__init__(file_name, action)
        self.ctype = ctype
        if self.is_tarfile:
            self.action = self.action + '|*'

    ############
    # BOOLEANS #
    ############
    @property
    def is_gzipped(self):
        """
        :return: Check if compression is gzip
        :rtype: bool
        """
        return self.ctype.endswith('gzip')

    @property
    def is_bzipped(self):
        """
        :return: Check if compression is bzip
        :rtype: bool
        """
        return self.ctype.endswith('bzip')

    @property
    def is_zipped(self):
        """
        :return: Check if compression is zip
        :rtype: bool
        """
        return self.ctype == 'zip'

    @property
    def is_tarfile(self):
        """
        :return: Check if compression is tar
        :rtype: bool
        """
        return self.ctype.startswith('tar')

    ####################
    # METHODS: ON FILE #
    ####################
    def open(self):
        """
        Open the file in the previously defined action type.
        :rtype: self
        """
        if self._is_open:
            return self
        self._is_open = True
        if self.is_tarfile:
            self._fd = tarfile.open(self.full)
        if self.is_zipped:
            self._fd = zipfile.ZipFile(self.full)
        return self

    def read_file(self, file_name):
        """
        Get a specific file from the file bundle.

        :param str file_name: Name of the query internal file.
        :raise: :py:class:`pynion.errors.fe.FileContainerFileNotFound` if query
            file is not in the bundle.
        :rtype: str
        """
        if self.is_zipped:
            if file_name not in self._fd.namelist():
                raise CNF(self.full, file_name)
            return self._fd.read(file_name).split('\n')
        if self.is_tarfile:
            if file_name not in self._fd.getnames():
                raise CNF(self.full, file_name)
            return self._fd.extractfile(self._fd.getmember(file_name)).readlines()

    def has_file(self, file_name):
        """
        Query if file exists in the bundle.

        :rtype: bool
        """
        if self.is_zipped:
            return file_name in self._fd.namelist()
        if self.is_tarfile:
            return file_name in self._fd.getnames()

    def extract(self, target_file = None, target_dir = os.getcwd()):
        """
        Extract a specific file from the bundle.

        :param str target_file: Query file to extract from the bundle. If
            :py:data:`None`, all files contained
        :param str target_dir: Directory to which to write the file. By default
            that is the current working directory
        :raise: :py:class:`pyninon.errors.fe.FileContainerFailedExtraction` if
            target_file not
        """
        if not os.path.isdir(target_dir) or not os.access(target_dir, os.W_OK):
            raise CFE(self.full, target_dir)
        if target_file is not None and not self.has_file(target_file):
            raise CNF(self.full, target_file)
        if target_file is None:
            self._fd.extractall(path = target_dir)
        else:
            self._fd.extract(target_file, target_dir)

    def list_files(self):
        """
        Name of all files in the bundle..
        :rtype: list
        """
        if self.is_tarfile: return self._fd.getnames()
        if self.is_zipped:  return self._fd.namelist()

    def length(self):
        """
        Number of lines in the file.
        :rtype: int
        """
        return len(self.list_files)
