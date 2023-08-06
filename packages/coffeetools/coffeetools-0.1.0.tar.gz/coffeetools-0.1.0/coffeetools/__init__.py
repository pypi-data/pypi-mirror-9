# python-coffeetools
#
# Various Tools for processing CoffeeScript from Python.
#
# Copyright (C) 2011-2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# python-coffeetools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-coffeetools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python-coffeetools.  If not, see <http://www.gnu.org/licenses/>.

"""coffeetools

Provides a Pythonic interface to the coffee binary.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['CoffeeError', 'Coffee', 'coffee']

from subprocess import Popen, PIPE

__version__ = '0.1.0'


class CoffeeError(Exception):
    pass


class Coffee(object):
    """Python interface to the ``coffee`` binary.

    - Evaluate CoffeeScript code by calling a :class:`Coffee` instance
      or `.compile()` to JavaScript.
    """
    def __call__(self, script, options=[]):
        """Evaluates a Coffee `script` string via ``coffee -s``
           and returns its output.

        - You can specify additional command line `options`
          as list of argument strings.
        """
        cmd = ['coffee', '-s']
        cmd += options
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output = p.communicate(script)
        if output[1]: # stderr
            raise CoffeeError(output[1])
        return output[0]

    def compile(self, script, bare=False):
        """Compile Coffee `script` string to JavaScript via ``coffee -c``

        - `bare` compiles without top-level function (adding ``-b`` flag)
        """
        options = ['-c']
        if bare:
            options.append('-b')
        return self(script, options=options)

    @property
    def version(self):
        """Get the version number string via ``coffee -v``
        """
        output = self('', options=['-v'])
        return output.rsplit(None, 1)[-1]


# Preinstantiated CoffeeScript interface.
coffee = Coffee()


def load_ipython_extension(shell):
    """Called on ``%load_ext coffeetools``
    """
    # import locally to avoid general dependency on IPython
    from .ipython import coffeescript
    shell.magics_manager.magics['cell']['coffeescript'] = coffeescript
