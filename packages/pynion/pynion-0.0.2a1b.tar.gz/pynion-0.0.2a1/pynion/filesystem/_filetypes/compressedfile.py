import bz2
import gzip

from .basefile import BaseFile


class CompressedFile(BaseFile):
    """
    The **CompressedFile** :py:class:`pynion.Multiton` is a file management object
    created directly through the py:class:`pynion.File` factory.

    Extends :py:class:`pynion.filesystem._filetypes.BaseFile`

    It specifically manages compressed files.

    """

    def __init__(self, file_name, action, ctype):
        super(CompressedFile, self).__init__(file_name, action)
        self.ctype = ctype

    ############
    # BOOLEANS #
    ############
    @property
    def is_gzipped(self):
        """
        :return: Check if compression is gzip
        :rtype: bool
        """
        return self.ctype == 'gzip'

    @property
    def is_bzipped(self):
        """
        :return: Check if compression is bzip
        :rtype: bool
        """
        return self.ctype == 'bzip'

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
        if self.is_gzipped:
            self._fd = gzip.open(self.full, self.action)
        elif self.is_bzipped:
            self._fd = bz2.BZ2File(self.full, self.action)
        return self

    def flush(self):
        """
        :raise: :py:class:`pynion.errors.fe.FileWrongRequestedActionError` if
            opened in read mode.
        """
        self._work_action('w')
        if self.is_bzipped:
            return
        self._fd.flush()
