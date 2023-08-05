import argparse
import datetime
import re

from . import Manager
m = Manager()


# User Options
def options(*args, **kwds):
    '''
    User options.

    @return: {Namespace}
    '''
    parser = argparse.ArgumentParser(prog            = 'pynion',
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter,
                                     description     = 'A library building minion')

    parser.add_argument('-p', '--project',      dest     = "project",
                        action  = "store",      required = True,
                        help    = "Project name")

    parser.add_argument('-c', '--config',       dest     = "configfile",
                        action  = "store",      required = False,
                        default = None,
                        help    = "Add a configuration file " +
                                  "for external software")
    parser.add_argument('-d', '--date',         dest     = "date",
                        action  = "store",      required = False,
                        default = datetime.date.today(),
                        help    = "Date of the project, as YYY-MM-DD")

    options = parser.parse_args()

    m.set_stdout()
    m.set_verbose()

    return options


if __name__ == "__main__":

    options = options()

    m.info('Creating project: {0}'.format(options.project))

    if isinstance(options.date, datetime.date):
        m.project.set_date()
    else:
        date_regex = re.compile('(\d{4})\-(\d{2})\-(\d{2})')
        d = date_regex.search(options.date)
        if not d:
            m.exception('Experiment date wrongly formated')
        m.project.set_date(d[1], d[2], d[3])

    m.project.set_configuration_file(options.configfile)
    m.project.create(options.project, m.experiment.user)
