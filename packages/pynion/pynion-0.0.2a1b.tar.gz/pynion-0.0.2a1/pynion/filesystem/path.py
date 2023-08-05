import os
import pathlib
import shutil

from ..          import Multiton
from ..          import Manager
from ..errors.pe import PathIsFile as PIF

m = Manager()


class Path(object):
    """
    The **Path** :py:class:`pynion.Multiton` is an extension (not an actual inheritance) from the
    :py:class:`pathlib.Path`.

    """
    __metaclass__ = Multiton

    _IDENTIFIER   = 'name'

    def __init__(self, name):
        """.. py:method:: __init__(name)

        Initializes the Path object. If the directory does not exist, it is
        created.

        :param str name: name of the directory.
        :raise: :py:class:`pynion.errors.pe.PathIsFile` if the given name is
            a file.
        """
        self.dname = pathlib.Path(name)
        if self.dname.is_file():
            raise PIF(self.full)
        if not self.dname.is_dir():
            self.mkdir()

    ##############
    # ATTRIBUTES #
    ##############
    @property
    def full(self):
        """
        :return: Full path of the directory
        :rtype: str
        """
        return str(self.dname.resolve())

    @property
    def parent(self):
        """
        :return: Name of parent directory
        :rtype: str
        """
        return str(self.dname.resolve().parent)

    @property
    def parents(self):
        """
        :return: Name of all parent directories
        :rtype: list
        """
        return self.dname.resolve().parents

    @property
    def name(self):
        """
        :return: Name of the directory
        :rtype: str
        """
        return str(self.dname.name)

    ###########
    # METHODS #
    ###########
    def relative_to(self, path = pathlib.Path.cwd()):
        """
        :param str path: Path to which the relative path is required.

        :return: Actual path relative to the query path
        :rtype: str
        """
        return self.dname.relative_to(path)

    def mkdir(self):
        """
        Create the directory of the path.

        Command is ignored if the directory already exists. Required parent
        directories are also created.
        """
        if self.dname.is_dir():
            m.warning('The directory {0} already exists.'.format(self.full))
        else:
            m.info('Creating directory {0}'.format(self.full))
            self.dname.mkdir(parents = True)

    def list_directories(self, rootless = False):
        """
        List all the directories inside the requested path.

        :param bool rootless: When :py:data:`True`, the directories are returned
            relative to the path. Full path otherwise.

        :rtype: iterator
        """
        def list_dir(path):
            for x in path.iterdir():
                if x.is_dir():
                    yield x
                    for y in list_dir(x):
                        yield y

        for x in list_dir(self.dname):
            yield self._rootless(x, rootless)

    def list_files(self, pattern     = '*',
                   avoid_empty_files = True, rootless = False):
        """
        List all the files inside the requested path.

        :param str pattern: Pattern to match the files (bash ls format).
        :param bool avoid_empty_files: When :py:data:`True`, empty files are omitted.
        :param bool rootless: When :py:data:`True`, the files are returned
            relative to the path. Full path otherwise.

        :rtype: iterator
        """
        search_patterns = []
        if not isinstance(pattern, list):
            search_patterns.append(pattern)
        else:
            search_patterns = pattern

        for pat in search_patterns:
            for x in self.dname.rglob(pat):
                if not x.is_file():
                    continue
                if not avoid_empty_files or x.stat().st_size > 0:
                    m.detail('Found file {0} with pattern {1}'.format(x, pat))
                    yield self._rootless(x, rootless)

    def do_files_match(self, pattern = '*', avoid_empty_files = True):
        """
        Search if files inside the directory match a given pattern.

        :param str pattern: Pattern to match the files (bash ls format).
        :param bool avoid_empty_files: When :py:data:`True`, empty files are omitted.
        :rtype: bool
        """
        for x in self.list_files(pattern = pattern,
                                 avoid_empty_files = avoid_empty_files):
            return True
        return False

    def compare_to(self, other, by_dir = True, by_file = False, as_string = False):
        """
        Compare the directory to another path.

        :param str other: Path to compare to.
        :param bool by_dir: Comparison by directories.
        :param bool by_file: Comparison by file. If :py:data:`True`, overrides
            *by_dir*.
        :param bool as_string: Formats the returned dict as a string.

        :rtype: dict
        """
        other, by_dir = self._prepare_comparisson(other, by_file)

        content = {self.full: [], other.full: []}
        full    = {}

        if by_dir:
            for onedir in self.list_directories(rootless  = True):
                content[self.full].append(onedir)
                content[other.full].append(None)
                full[onedir] = len(content[self.full]) - 1
            for onedir in other.list_directories(rootless = True):
                if onedir in full:
                    content[other.full][full[onedir]] = onedir
                else:
                    content[self.full].append(None)
                    content[other.full].append(onedir)
        elif by_file:
            for onedir in self.list_files(rootless  = True):
                content[self.full].append(onedir)
                content[other.full].append(None)
                full[onedir] = len(content[self.full]) - 1
            for onedir in other.list_files(rootless = True):
                if onedir in full:
                    content[other.full][full[onedir]] = onedir
                else:
                    content[self.full].append(None)
                    content[other.full].append(onedir)

        if not as_string:
            return content
        else:
            data = [self.full + '\t' + other.full]
            for c in range(len(content[self.full])):
                c1 = str(content[self.full][c])
                c2 = str(content[other.full][c])
                data.append(c1 + '\t' + c2)
            return '\n'.join(data)

    def sync_to(self, other, by_dir = True, by_file = False):
        """
        Sync from directory to another path.

        :param str other: Path to sync with.
        :param bool by_dir: Sync by directories.
        :param bool by_file: Sync by file. If :py:data:`True`, overrides
            *by_dir*.
        """
        other, by_dir = self._prepare_comparisson(other, by_file)

        diff = self.compare_to(other, by_dir, by_file)
        for i in range(len(diff[self.full])):
            if diff[other.full][i] is None:
                source      = self.dname  / diff[self.full][i]
                destination = other.dname / diff[self.full][i]
                Path._copy(source, destination, by_file)

    def sync_from(self, other, by_dir = True, by_file = False):
        """
        Sync from another path to the directory.

        :param str other: Path to sync with.
        :param bool by_dir: Sync by directories.
        :param bool by_file: Sync by file. If :py:data:`True`, overrides
            *by_dir*.
        """
        other, by_dir = self._prepare_comparisson(other, by_file)

        diff = self.compare_to(other, by_dir, by_file)
        for i in range(len(diff[self.full])):
            if diff[self.full][i] is None:
                source      = other.dname / diff[other.full][i]
                destination = self.dname  / diff[other.full][i]
                Path._copy(source, destination, by_file)

    ####################
    # METHODS: PRIVATE #
    ####################
    @staticmethod
    def _copy(source, destination, by_file):
        if os.path.exists(str(destination)):
            return
        m.debug('Copy {0} to {1}'.format(str(source), str(destination)))
        if not by_file:
            shutil.copytree(str(source), str(destination))
        elif by_file:
            if not destination.parent.exists():
                destination.parent.mkdir(parents = True)
            shutil.copyfile(str(source), str(destination))

    def _prepare_comparisson(self, other, by_file):
        if isinstance(other, basestring):
            other  = Path(other)
        elif isinstance(other, pathlib.Path):
            other  = Path(str(other.resolve()))

        return other, not by_file

    def _rootless(self, path, rootless):
        if path is None:
            return 'None'
        if not rootless:
            return str(path)
        else:
            return str(path.relative_to(self.dname))
