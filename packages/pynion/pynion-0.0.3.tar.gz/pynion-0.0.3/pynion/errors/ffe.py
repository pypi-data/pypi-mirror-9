# FileFactoryErrors


class FileFactoryError(Exception):
    def __init__(self, filename, action):
        self.filename = filename
        self.action   = action
        if self.action   == 'r': self.action = 'read'
        elif self.action == 'w': self.action = 'write'


class FileAccessError(FileFactoryError):
    def __str__(self):
        return '{0.action} access to {0.filename} not allowed'.format(self)


class FileDirNotExistError(FileFactoryError):
    def __str__(self):
        return 'Can\'t write {0.filename} containing directory does not exist'.format(self)


class FileIsDirError(FileFactoryError):
    def __str__(self):
        return '{0.filename} is a directory'.format(self)


class FileNotExistsError(FileFactoryError):
    def __str__(self):
        return '{0.filename} does not exist'.format(self)


class FileOverwriteError(FileFactoryError):
    def __str__(self):
        return '{0.filename} already exists. Overwrite not allowed'.format(self)


class FileWrongActionError(FileFactoryError):
    def __str__(self):
        return '{0.action} is not an acceptable action for File'.format(self)


class FileWrongPatternIDError(FileFactoryError):
    def __str__(self):
        return '\n'.join(['{0.action} cannot be used as a identifier'.format(self),
                          'The object already contains an attribute/method with that name'])


class FileWrongPatternFormatError(FileFactoryError):
    def __str__(self):
        return '{0.action} does not match the name format of {0.filename}'.format(self)
