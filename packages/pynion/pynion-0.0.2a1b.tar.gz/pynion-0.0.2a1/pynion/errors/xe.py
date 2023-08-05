# Executable Error


class ExecutableError(Exception):
    def __init__(self, info):
        self.info = info


class ExecutableNoExistsError(ExecutableError):
    def __str__(self):
        return '{0.info} does not exist'.format(self)


class ExecutableNotInPathError(ExecutableError):
    def __str__(self):
        return '{0.info} cannot be found in the system\'s path'.format(self)


class ExecutablePermissionDeniedError(ExecutableError):
    def __str__(self):
        return 'Permission to execute {0.info} denied'.format(self)
