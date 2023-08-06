================================
Generalized Package Asset Loader
================================

Loads resources and symbols from a python package, whether installed
as a directory, an egg, or in source form. Also provides some other
package-related helper methods, including ``asset.version()`` and
``asset.caller()``.

TL;DR
=====

Install:

.. code-block:: bash

  $ pip install asset

Load symbols (e.g. functions, classes, or variables) from a package by
name:

.. code-block:: python

  import asset

  # load the 'mypackage.foo.myfunc' function and call it with some parameter
  retval = asset.symbol('mypackage.foo.myfunc')(param='value')

Load data files from a package:

.. code-block:: python

  # load the file 'mypackage/templates/data.txt' into string
  data = asset.load('mypackage:templates/data.txt').read()

  # or as a file-like stream
  stream = asset.load('mypackage:templates/data.txt').stream()
  data   = stream.read()

Multiple files can be operated on at once by using `globre
<https://pypi.python.org/pypi/globre>`_ style wildcards:

.. code-block:: python

  # concatenate all 'css' files into one string:
  css = asset.load('mypackage:static/style/**.css').read()

  # load all '.txt' files, XML-escaping the data and wrapping
  # each file in an <node name="...">...</node> element.
  import xml.etree.ElementTree as ET
  data = ET.Element('nodes')
  for item in asset.load('asset:**.txt'):
    cur = ET.SubElement(data, 'node', name=item.name)
    cur.text = item.read()
  data = ET.tostring(data)

Query the installed version of a package:

.. code-block:: python

  asset.version('asset')
  # ==> '0.0.5'

  asset.version('python')
  # ==> '2.7'

  asset.version('no-such-package')
  # ==> None

Find out what package is calling the current function:

.. code-block:: python

  # assuming the call stack is:
  #   in package "zig" a function "x", which calls
  #   in package "bar" a function "y", which calls
  #   in package "foo" a function "callfoo" defined as:

  def callfoo():

    asset.caller()
    # ==> 'bar'

    asset.caller(ignore='bar')
    # ==> 'zig'

    asset.caller(ignore=['bar', 'zig'])
    # ==> None


Details
=======

TODO: add detailed docs...

* ``Asset.filename``:

  If the asset represents a file on the filesystem, is the absolute
  path to the specified file. Otherwise is ``None``.

* ``AssetGroupStream.readline()``:

  Returns the next line from the aggregate asset group stream, as if
  the assets had been concatenate into a single asset.

  **IMPORTANT**: if an asset ends with content that is not terminated
  by an EOL token, it is returned as-is, i.e. it does NOT append the
  first line from the next asset.

Note: because ``asset.load()`` does lazy-loading, it only throws a
`NoSuchAsset` exception when you actually attempt to use the
AssetGroup! If you need an immediate error, use the `peek()` method.
Note that it returns itself, so you can do something like:

.. code-block:: python

  import asset

  def my_function_that_returns_an_iterable():

    return asset.load(my_spec).peek()

    # this returns exactly the same thing as the following:
    #
    #   return asset.load(my_spec)
    #
    # but throws an exception early if there are no matching assets.
