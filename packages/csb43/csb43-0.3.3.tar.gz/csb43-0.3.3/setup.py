from __future__ import print_function
from __future__ import unicode_literals

import os
import codecs
from setuptools import find_packages, setup
import csb43
from csb43.utils import IS_PY3

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top
# level README file and 2) it's easier to type in the README file than to put
# a raw string in below ...


def read(fname):
    try:
        with codecs.open(os.path.join(os.path.dirname(__file__), fname),
                         'r', 'utf-8') as f:
            return f.read()
    except:
        return ''

try:
    from babel.messages import frontend as babel

    entry_points = """
    [distutils.commands]
    compile_catalog = babel:compile_catalog
    extract_messages = babel:extract_messages
    init_catalog = babel:init_catalog
    update_catalog = babel:update_catalog
    """
except ImportError:
    pass

config = {'name': "csb43",
          'version': csb43.__version__,
          'author': "wmj",
          'author_email': "wmj.py@gmx.com",
          'description': csb43.__doc__,
          'license': "LGPL",
          'keywords': "csb csb43 aeb aeb43 homebank ofx Spanish bank ods tsv "
                      "xls xlsx excel yaml json html",
          'url': "https://bitbucket.org/wmj/csb43",
          'packages': find_packages(),
          'long_description': (read('_README.rst') +
                               read('INSTALL') +
                               read('CHANGELOG')),
          'scripts': ["csb2format"],
          'requires': ["pycountry", "PyYAML", "simplejson"],
          'install_requires': ["pycountry", "PyYAML", "simplejson"],
          'include_package_data': True,
          'extras_require': {
              'babel': ["Babel"],
          },
          'test_suite': 'csb43.tests',
          #'package_data': {
          #    'i18n': ['csb43/i18n/*']
          #},
          'classifiers': ["Programming Language :: Python",
                          "Programming Language :: Python :: 3",
                          "Development Status :: 4 - Beta",
                          "Environment :: Console",
                          "Topic :: Utilities",
                          "Topic :: Office/Business :: Financial",
                          "License :: OSI Approved :: GNU Lesser General "
                          "Public License v3 (LGPLv3)"]
}

if not IS_PY3:
    config['requires'].append('tablib')
    config['install_requires'].append('tablib')


try:
    import py2exe

    config['console'] = ["csb2format"]
    config['options'] = {"py2exe": {"bundle_files": 1}}
    config['zipfile'] = None
except ImportError:
    pass


setup(**config)
