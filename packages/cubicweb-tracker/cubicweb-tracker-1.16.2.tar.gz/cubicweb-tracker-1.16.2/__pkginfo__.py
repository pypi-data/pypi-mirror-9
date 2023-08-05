# -*- encoding: utf-8 -*-
# pylint: disable-msg=W0622
"""cubicweb-tracker application packaging information

Copyright (c) 2003-2013 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr

---

The Entypo pictograms are licensed under CC BY 3.0 and the font under
SIL Open Font License.

The rights to each pictogram in the social extention are either
trademarked or copyrighted by the respective company.

Entypo pictograms by Daniel Bruce — www.entypo.com
"""
modname = 'tracker'
distname = 'cubicweb-tracker'

numversion = (1, 16, 2)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'basic tracker with project, version, ticket for the CubicWeb framework'
web = 'http://www.cubicweb.org/project/%s' % distname
classifiers = [
          'Environment :: Web Environment',
          'Framework :: CubicWeb',
          'Programming Language :: Python',
          'Programming Language :: JavaScript',
          'Topic :: Software Development :: Bug Tracking',
]

__depends__ = {'cubicweb': '>= 3.19.4',
               'cubicweb-activitystream': None,
               'cubicweb-localperms': None,
               'cubicweb-iprogress': None,
               }
__recommends__ = {'cubicweb-preview': None}

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

