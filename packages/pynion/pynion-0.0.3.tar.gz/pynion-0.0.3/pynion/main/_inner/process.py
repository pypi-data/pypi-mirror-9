"""

@author: Jaume Bonet
@mail:   jaume.bonet@gmail.com
@date:   2014

@ [oliva's lab](http://sbi.imim.es)

"""


class Process(object):
    ''' Data structure for a processes . The class properties are
    process attributes '''
    def __init__(self, proc_info):
        self.user  = proc_info[0]
        self.pid   = int(proc_info[1])
        self.cpu   = proc_info[2]
        self.mem   = proc_info[3]
        self.vsz   = proc_info[4]
        self.rss   = proc_info[5]
        self.tty   = proc_info[6]
        self.stat  = proc_info[7]
        self.start = proc_info[8]
        self.time  = proc_info[9]
        self.cmd   = ' '.join(proc_info[10:])

    #################
    # CLASS METHODS #
    #################
    def __str__(self):
        ''' Returns a string containing minimalistic info
        about the process : user, pid, and command '''
        return '{0.user} {0.pid} {0.cmd}'.format(self)

    def __repr__(self):
        return str(self)
