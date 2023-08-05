import os

import pathlib

from ..           import Manager
from ..errors.ffe import FileAccessError             as FAE
from ..errors.ffe import FileDirNotExistError        as FDN
from ..errors.ffe import FileIsDirError              as FID
from ..errors.ffe import FileNotExistsError          as FNE
from ..errors.ffe import FileOverwriteError          as FOE
from ..errors.ffe import FileWrongActionError        as FWA
from ..errors.ffe import FileWrongPatternIDError     as WPI
from ..errors.ffe import FileWrongPatternFormatError as WPF
from ._filetypes  import BaseFile, CompressedFile, ContainerFile

m = Manager()


class File(object):
    """
    The **File** object is a *factory object pattern* that creates either a
    :py:class:`pynion.filesystem._filetypes.BaseFile`, a
    :py:class:`pynion.filesystem._filetypes.CompressedFile` or a
    :py:class:`pynion.filesystem._filetypes.ContainerFile`.

    :param str file_name: Name of the file.
    :param str action: Action to perform to the file ('r', 'w', 'a', 't').
    :param bool overwrite: Specific overwrite policy over the file. By default,
        it uses the value of :py:class:`pynion.Manager` :py:data:`overwrite`.
    :param bool temp: Register the file as a temporary file, which means that it
        will be erased at the end of the execution unless
        :py:class:`pynion.Manager` :py:data:`clean` is set to :py:data:`False`.
    :param str pattern: A pattern to match sections of the file name to attributes
        in the generated object.
    :raise: :py:class:`pynion.errors.ffe.FileAccessError` if asked for a
        file without the right user permissions.
    :raise: :py:class:`pynion.errors.ffe.FileDirNotExistError` if asked to write
        a file in a directory that does not exist.
    :raise: :py:class:`pynion.errors.ffe.FileIsDirError` if path is a directory.
    :raise: :py:class:`pynion.errors.ffe.FileNotExistsError` if asked to read
        a files that does not exists.
    :raise: :py:class:`pynion.errors.ffe.FileOverwriteError` if asked to write
        a file that already exist and own :py:data:`overwrite` or
        :py:class:`pynion.Manager` :py:data:`overwrite` are :py:data:`False`.
    :raise: :py:class:`pynion.errors.ffe.FileWrongActionError` when asked for an
        unknown action.
    :raise: :py:class:`pynion.errors.ffe.FileWrongPatternIDError` if names in the
        pattern match names of attributes that exist in the returned class.
    :raise: :py:class:`pynion.errors.ffe.FileWrongPatternFormatError` if the given
        pattern cannot be matched to the file name.
    """

    ACTIONS    = frozenset(['r', 'w', 'a', 't'])
    COMPRESSED = {'.gz':   'gzip',    '.bz2':     'bzip'}
    CONTAINER  = {'.tar':  'tar',     '.tgz':     'targzip', '.zip': 'zip',
                  '.tbz2': 'tarbzip', '.tar.gz':  'targzip',
                  '.tb2':  'tarbzip', '.tar.bz2': 'tarbzip'}

    def __new__(cls, file_name, action = 't',
                overwrite = None, temp = False, pattern = None):
        f = pathlib.Path(file_name)
        if f.is_dir():  # File is a directory
            raise FID(file_name, action)
        if action not in cls.ACTIONS:  # Wrong requested action for file
            raise FWA(file_name, action)
        if action == 't':  # TOUCH
            if f.is_file():
                m.info('{0} exists'.format(file_name))
            else:
                f.touch()
                m.info('{0} created'.format(file_name))
            return
        if action == 'w' or action == 'a':  # WRITE
            if f.is_file():  # Overwrite must be allowed if the file exists
                if not m.evaluate_overwrite(overwrite):
                    raise FOE(file_name, action)
                if not os.access(f, os.W_OK):
                    raise FAE(file_name, action)
            else:
                if not f.parent.exists():
                    raise FDN(str(f), action)
                if not os.access(str(f.parent), os.W_OK):
                    raise FAE(str(f.parent), action)
        elif action == 'r':  # READ
            if not f.is_file():  # Read a file that does not exist
                raise FNE(file_name, action)
            if not os.access(str(f.resolve()), os.R_OK):
                raise FAE(file_name, action)
        if not temp:
            m.add_experiment_file(file_name, action)
        else:
            m.add_temporary_file(file_name)

        # Decide FileType
        sfxs = f.suffixes
        if sfxs[-1] in cls.CONTAINER:
            m.info('Declaring Container File: {0}'.format(file_name))
            newfile = ContainerFile(file_name, action + 'b',
                                    cls.CONTAINER[sfxs[-1]])
        elif len(sfxs) > 1 and '.'.join(sfxs[-2:]) in cls.CONTAINER:
            m.info('Declaring Container File: {0}'.format(file_name))
            newfile = ContainerFile(file_name, action,
                                    cls.CONTAINER[sfxs[-2:]])
        elif sfxs[-1] in cls.COMPRESSED:
            m.info('Declaring Compressed File: {0}'.format(file_name))
            newfile = CompressedFile(file_name, action + 'b',
                                     cls.COMPRESSED[sfxs[-1]])
        else:
            m.info('Declaring Regular File: {0}'.format(file_name))
            newfile = BaseFile(file_name, action)

        # Create FileName Pattern access
        if pattern is not None:
            fparts = f.name.split('.')
            pparts = pattern.split('.')
            if len(pparts) > len(fparts):
                raise WPF(file_name, pattern)
            classdefined = dir(newfile)
            print classdefined
            for i in range(len(pparts)):
                if pparts[i] not in classdefined:
                    newfile.__dict__[pparts[i]] = fparts[i]
                else:
                    raise WPI(file_name, pparts[i])
            newfile._pattern = pparts

        return newfile
