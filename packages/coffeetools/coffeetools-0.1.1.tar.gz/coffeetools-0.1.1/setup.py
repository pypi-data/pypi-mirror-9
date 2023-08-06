import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, ROOT)

import coffeetools


EXTRAS = {
  extra: open(os.path.join(ROOT, 'requirements.%s.txt' % extra)).read()
  for extra in ['jinja', 'ipython']}
EXTRAS['all'] = '\n'.join(EXTRAS.values())


setup(
  name='coffeetools',
  version=coffeetools.__version__,
  description=(
    'Tools for using CoffeeScript with Python.'
    ),
  author='Stefan Zimmermann',
  author_email='zimmermann.code@gmail.com',
  url='http://bitbucket.org/userzimmermann/python-coffeetools',

  license='LGPLv3',

  extras_require=EXTRAS,

  packages=[
    'coffeetools',
    'coffeetools.jinja',
    'coffeetools.ipython',
    ],

  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved ::'
    ' GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Utilities',
    ],
  keywords=[
    'coffee', 'tools', 'script', 'coffeescript', 'javascript',
    'jinja', 'jinja2', 'jinjatools', 'template', 'tag', 'extension',
    'python3',
    ],
  )
