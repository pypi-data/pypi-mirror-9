# MetaclassErrors


class MetaclassError(Exception):
    def __init__(self, info):
        self.info = info


class BadMultitonIdentifier(MetaclassError):
    def __str__(self):
        data = ['{0.info[0]} probably is not a good identifier to distinguish',
                'multitones of {0.info[1]}. It might possible not even be',
                'one of the __init__ parameters of the object.',
                'Re-check your object definition.']
        return ' '.join(data).format(self).replace('. ', '.\n')
