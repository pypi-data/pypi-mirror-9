CoffeeScript from Python
========================

[https://bitbucket.org/userzimmermann/python-coffeetools]()

* [`coffee`][1] interface for evaluating and compiling
  [CoffeeScript](http://coffeescript.org/)

* [`{% coffee ... %}`][2] template tags for [Jinja2](http://jinja.pocoo.org)

* [`%%coffeescript`][3] magic function for [IPython Notebook](
    http://ipython.org/notebook.html)


0. Setup
--------

Supported Python versions: __2.7__ and __3.3+__

You need an installed CoffeeScript compiler.
By default __coffeetools__ look for a `coffee` executable in your `PATH`,
or `coffee.cmd` on Windows.
You can find installation instructions and further information at
[http://coffeescript.org/]().
The easiest way is to use the
[node package manager](https://www.npmjs.com/):

    npm install coffee-script

To install __coffeetools__, just use [pip](http://www.pip-installer.org)
to get the latest [release](https://pypi.python.org/pypi/coffeetools)
from [PyPI](https://pypi.python.org):

    pip install coffeetools

For basic usage there are no dependencies on other Python packages.

__Jinja__ and __IPython__ integration are `[extra]` features.
They require the following Python packages:

* `[jinja]`

    * [`jinjatools >= 0.1.4`](https://pypi.python.org/pypi/jinjatools)

* `[ipython]`

    * [`ipython[notebook]`](https://pypi.python.org/pypi/ipython)

All extra Python requirements can also be installed with:

    pip install coffeetools[all]


1. Using CoffeeScript from Python
---------------------------------
[1]: #markdown-header-1-using-coffeescript-from-python

    from coffeetools import coffee

Evaluate CoffeeScript code and return the script's output:

    coffee('Some CoffeeScript')

Compile CoffeeScript to JavaScript:

    coffee.compile('Some CoffeeScript')

Compile CoffeeScript to JavaScript without a top-level `function()`:

    coffee.compile('Some CoffeeScript', bare=True)

If you want to specify a custom name
of your CoffeeScript compiler executable or its absolute or relative path,
just create a custom interface instance:

    from coffeetools import Coffee

    coffee = Coffee('executable')
    #OR
    coffee = Coffee('/absolute/path/to/executable')
    #OR
    coffee = Coffee('relative/path/to/executable')


2. Using CoffeeScript from Jinja2
---------------------------------
[2]: #markdown-header-2-using-coffeescript-from-jinja2

More information coming soon...


3. Evaluate CoffeeScript in an IPython Notebook
-----------------------------------------------
[3]: #markdown-header-3-evaluate-coffeescript-in-an-ipython-notebook

    %load_ext coffeescript

It is also safe to `%reload_ext coffeescript`

This registers the `%%coffeescript` cell magic function,
which works like Ipython's `%%javascript` magic,
except that it takes CoffeeScript as input.
It compiles the given code to JavaScript
and uses `IPython.display.display()` with `IPython.display.Javascript`
to run the code directly in the browser window:

    %%coffeescript
    alert $('#notebook_name').text()