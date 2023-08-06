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

"""coffeetools.ipython

%%coffeescript cell magic for IPython.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

import sys

from IPython.display import display, Javascript


def coffeescript(options_text, cell_text):
    """The %%coffeescript cell magic function.
    """
    # import locally to NOT stick with old objects
    # after %reload_ext coffeetools
    from coffeetools import coffee, CoffeeError
    try:
        javascript = coffee.compile(cell_text)
    except CoffeeError as e:
        sys.stderr.write(str(e))
        sys.stderr.flush()
    else:
        display(Javascript(javascript))
