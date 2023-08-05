# pylint: disable=W0622
"""cubicweb-apycot application packaging information"""

modname = 'apycotlib'
distname = 'apycot'

numversion = (3, 2, 1)
version = '.'.join(str(num) for num in numversion)

license = 'GPL'
description = 'Continuous testing / integration tool for the CubicWeb framework'
author = 'Logilab'
author_email = 'contact@logilab.fr'
web = 'http://www.logilab.org/project/apycot'
classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

__depends__ = {'cubicweb': '>= 3.19.0',
               'cubicweb-vcsfile': '>= 2',
               'cubicweb-file': None,
               'cubicweb-narval': '>= 4.1',
               'Pygments': None,
               'lxml': None,
               }
__recommends__ = {'cubicweb-tracker': None,
                  'cubicweb-nosylist': '>= 0.5.0',
                  'cubicweb-jqplot': '>= 0.1.2',
                  'logilab-devtools': None,
                  'coverage': None,
                  }

# packaging ###

from os import listdir as _listdir
from os.path import join, isdir, dirname
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', distname)

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
for subdir in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration', 'wdoc'):
    if isdir(subdir):
        data_files.append([join(THIS_CUBE_DIR, subdir), listdir(subdir)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

NARVALDIR = join(dirname(__file__), '_narval')
if isdir(NARVALDIR): # test REQUIRED (to be importable from everywhere)
    data_files.append([join('share', 'narval', 'checkers'),
                       listdir(join(NARVALDIR, 'checkers'))])
    data_files.append([join('share', 'narval', 'checkers', distname),
                       listdir(join(NARVALDIR, 'checkers', distname))])
    data_files.append([join('share', 'narval', 'preprocessors'),
                       listdir(join(NARVALDIR, 'preprocessors'))])
    data_files.append([join('share', 'narval', 'preprocessors', distname),
                       listdir(join(NARVALDIR, 'preprocessors', distname))])
if isdir(join(NARVALDIR, 'data')): # test REQUIRED (to be importable from everywhere)
    data_files.append([join('share', 'narval', 'data'),
                       listdir(join(NARVALDIR, 'data'))])
