"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""
import collections
import datetime
import json
import os
import shutil

from ...metaclass import Singleton


class Project(object):
    __metaclass__  = Singleton

    def __init__(self, project_file, config_file, pipeline_file):
        # Default Project Conditions:
        self.name           = None
        self.author         = None
        self.description    = None
        self.citation       = None
        self.working_dir    = os.getcwd()
        self.date           = None

        self.is_active      = False

        self._configfile    = None

        self._project_file  = project_file
        self._config_file   = config_file
        self._pipeline_file = pipeline_file

        self._reactivate()

    @property
    def project_file(self):
        return os.path.join(self.working_dir, self._project_file)

    @property
    def configuration_file(self):
        return os.path.join(self.working_dir, self._config_file)

    @property
    def pipeline_file(self):
        return os.path.join(self.working_dir, self._pipeline_file)

    ####################
    # METHODS: SETTERS #
    ####################
    def set_date(self, year=None, month=None, day=None):
        from .. import Manager
        m = Manager()

        if year is None and month is None and day is None:
            m.info('Today is setted as the Project\'s timestamp.')
            self.date = datetime.date.today()
        elif year is None or month is None or day is None:
            m.exception(['Either no parameter is defined and date is set to today.',
                         'Or all the parameters year, month, day need to be defined.'])
        else:
            self.date = datetime.date(year, month, day)

    def set_configuration_file(self, filename):
        if filename is None:
            return
        if not os.path.isfile(filename):
            from .. import Manager
            m = Manager()
            m.exception(IOError('file {0} does not exist'.format(filename)))
        self._configfile = filename

    ######################
    # METHODS: REPRESENT #
    ######################
    def summary(self):
        if not self.is_active:
            return

        from ..import Manager
        m = Manager()

        data  = ['# Project:',
                 '# Title: {0}'.format(self.name),
                 '# By: {0}'.format(self.author)]
        if self.description is not None:
            data.append('# Is: {0}'.format(self.description))
        if self.citation is not None:
            data.append('# Cite: {0}'.format(self.citation))
        if self.date is not None:
            data.append('# TimeStamp: {0}'.format(self.date.isoformat()))
        m.info(data)

    #######################
    # METHODS: ACTIVATION #
    #######################
    def create(self, name, author):
        from .. import Manager
        m = Manager()
        if os.path.isfile(self.project_file):
            m.exception(['A project already exists in this folder',
                         'Create a new project in a new folder.'])
        if self.date is None:
            m.exception('A date must be added for a new project to be created.')
        if os.path.isfile(self.pipeline_file):
            m.exception(['A collection of executions already exist in this dir',
                         'Create a new project in a new folder.'])

        data = collections.OrderedDict()
        data['name']        = name
        data['author']      = author
        data['date']        = self.date.isoformat()
        data['description'] = self.description
        data['citation']    = self.citation

        m.info(['Creating project file:',
                '{0}.'.format(self.project_file)])
        fd = open(self.project_file, 'w')
        fd.write(json.dumps(data, indent=4, separators=(',', ':')))
        fd.close()

        m.info(['Creating experiments file:',
                '{0}.'.format(self.pipeline_file)])
        fd = open(self.pipeline_file, 'w')
        fd.close()

        if self._configfile is None:
            m.info(['Creating empty configuration file:',
                    '{0}.'.format(self.configuration_file)])
            fd = open(self.configuration_file, 'w')
            fd.close()
        else:
            m.info(['Copy predefined configuration file:',
                    '{0}.'.format(self._configfile),
                    'Into configuration file:',
                    '{0}.'.format(self.configuration_file)])
            shutil.copyfile(self._configfile, self.configuration_file)

        self.is_active = True

    def _reactivate(self):
        if not os.path.isfile(self.project_file):
            return
        self.is_active = True
