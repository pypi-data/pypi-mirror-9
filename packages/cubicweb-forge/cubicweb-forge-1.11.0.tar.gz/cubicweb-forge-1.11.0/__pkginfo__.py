# pylint: disable-msg=W0622
"""cubicweb-forge application packaging information"""
modname = 'forge'
distname = 'cubicweb-forge'

numversion = (1, 11, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'software forge component for the CubicWeb framework'
web = 'http://www.cubicweb.org/project/%s' % distname
classifiers = [
          'Environment :: Web Environment',
          'Framework :: CubicWeb',
          'Programming Language :: Python',
          'Programming Language :: JavaScript',
          'Topic :: Software Development :: Bug Tracking',
          ]

__depends__ = {'cubicweb': '>= 3.16.0',
               'cubicweb-card': None,
               'cubicweb-comment': '>= 1.2.0',
               'cubicweb-email': '>= 1.2.1',
               'cubicweb-file': '>= 1.2.0',
               'cubicweb-folder': '>= 1.1.0',
               'cubicweb-mailinglist': '>= 1.1.0',
               'cubicweb-tag': '>= 1.2.0',
               'cubicweb-testcard': None,
               'cubicweb-tracker': '>= 1.12.0',
               'cubicweb-nosylist': None,
               'Pillow': None,
               }


# packaging ###

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration', 'wdoc'):
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package
