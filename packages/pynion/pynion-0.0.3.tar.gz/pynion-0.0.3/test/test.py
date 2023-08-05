from pynion import *
m = Manager()
# m.set_stdout()
# m.set_debug()
# import sys

# m.info('hi')
# import sys
# print sys.executable
# print sys.version_info[:3]
# print ' '.join(sys.argv)
# import os
# print os.getcwd()

# from collections import OrderedDict
# a = OrderedDict()
# a = OrderedDict({'a': 1, 'b': 2, 'c': 3, 'r': 6, 'd': [5})
# print a
# n = Manager()
# print m is n
# print m is m.experiment
# print type(m)
# print type(m.experiment)


# class Test(Manager):
#     pass

# t = Test()
# print type(t)
# print t is m
# a = TempFile('d', 'n')
# b = File('a.txt', 'r', pattern='prot.ext')
# c = File('d.txt.gz', 'r', pattern='prot.ext')
# f = File('d.txt.gz', 'r')
# # print type(a)
# # print type(b)
# print type(b)
# print b.__class__
# print dir(b)
# print b.prot, b.ext
# print type(c)
# print c.__class__
# print c.prot
# print type(f)
# print f.__class__
# print f.prot
# print f.pattern
# print c is f
# print c
# print repr(c)
# # print a is b
# # print a is c
# # print a.instance

# fd = File('Q9Y2J8.txt.gz', 'r').open()
# # fd.open()
# for l in fd.read():
#     print l.strip()
# fd.close()
# print fd.is_open
# import numpy as np


# class V(object):
#     def __init__(self):
#         self.d = np.array([1, 2, 3])

#     def __str__(self):
#         return repr(self.d)


# class Test(JSONer):
#     def __init__(self):
#         self.a = 1
#         self.b = 'string'
#         self.c = ['a', 'b']
#         self.d = set(self.c)
#         self.e = V()
#         self.f = np.float64(23)
#         self.g = np.matrix([[1, 2], [3, 4]])

#     def __str__(self):
#         data = []
#         for d in sorted(self.__dict__):
#             data.append(' - '.join([d, str(self.__dict__[d])]))
#         return '\n'.join(data)

# a = Test()
# print a
# print a.to_json(api = True)
# b = Test.from_json(a.to_json(api = True))
# print b
# print type(b.e.d)
# print type(b.g)
# fd = File('Q9Y2J8.2.txt')
# a = Path(sys.argv[1])
# # for d in a.list_files(pattern = '*Amics*'):
# #     print d
# b = Path(sys.argv[2])
# print a.sync_from(b, by_file=True)
