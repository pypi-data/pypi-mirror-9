# FileErrors


class FileError(Exception):
    def __init__(self, filename, action):
        self.filename = filename
        self.action   = action
        if self.action   == 'r': self.action = 'read'
        elif self.action == 'w': self.action = 'write'


class FileOpenError(FileError):
    def __str__(self):
        return '{0.filename} is not open'.format(self)


class FileWrongRequestedActionError(FileError):
    def __str__(self):
        return 'Unable to perform the action. {0.filename} is open to {0.action}'.format(self)


class FileContainerFileNotFound(FileError):
    def __str__(self):
        return '{0.action} not in {0.filename}'.format(self)


class FileContainerFailedExtraction(FileError):
    def __str__(self):
        return '{0.filename} cannot be extracted to {0.action}'.format(self)
