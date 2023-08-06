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

"""coffeetools.jinja

Provides the :class:`CoffeeExtension`,
which adds a Jinja {% coffee ... %} template tag
for evaluating CoffeeScript or compiling it to JavaScript.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['CoffeeExtension']

from jinjatools.ext import TagExtension

from coffeetools import coffee


class CoffeeExtension(TagExtension):
    """The {% coffee ... %} tag.
    """
    def __init__(self, environment):
        TagExtension.__init__(self, environment)
        environment.extend(
          coffee_compile_bare=False,
          )

    def tag_coffee(self, caller):
        """{% coffee %} script {% endcoffee %}

        - Evaluates script and returns output.
        """
        return coffee(caller())

    def tag_coffee_compile(self, caller):
        """{% coffee compile %} script {% endcoffee %}

        - Compiles script with top-level function and returns JavaScript.
        """
        return coffee.compile(
          caller(), bare=self.environment.coffee_compile_bare)

    def tag_coffee_compile_bare(self, caller):
        """{% coffee compile bare %} script {% endcoffee %}

        - Compiles script without top-level function and returns JavaScript.
        """
        return coffee.compile(caller(), bare=True)
