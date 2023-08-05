# PathErrors


class PathError(Exception):
    def __init__(self, info):
        self.info = info


class PathIsFile(PathError):
    def __str__(self):
        return '{0.info} is a file, not a directory'.format(self)
