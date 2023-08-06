Graphviz
========

|PyPI version| |License| |Supported Python| |Format| |Downloads|

This package facilitates the creation of graph descriptions in the DOT_ language
of the Graphviz_ graph drawing software from Python.

Create a graph object, assemble the graph by adding nodes and edges, and
retrieve its DOT source code string. Save the source code to a file and render
it with the Graphviz installation of your system.

Use the ``view`` option/method to directly inspect the resulting (PDF, PNG,
SVG, etc.) file with its default application.


Links
-----

- GitHub: http://github.com/xflr6/graphviz
- PyPI: http://pypi.python.org/pypi/graphviz
- Download: http://pypi.python.org/pypi/graphviz#downloads
- Documentation: http://graphviz.readthedocs.org
- Changelog: http://graphviz.readthedocs.org/en/latest/changelog.html
- Isssue Tracker: http://github.com/xflr6/graphviz/issues


Installation
------------

This package runs under Python 2.7 and 3.3+, use pip_ to install:

.. code:: bash

    $ pip install graphviz

To render the generated DOT source code, you also need to install Graphviz
(`download page`_).

Make sure that the ``dot`` executable is on your systems' path.


Quickstart
----------

Create a graph object:

.. code:: python

    >>> from graphviz import Digraph

    >>> dot = Digraph(comment='The Round Table')

    >>> dot  #doctest: +ELLIPSIS
    <graphviz.dot.Digraph object at 0x...>

Add nodes and edges:

.. code:: python

    >>> dot.node('A', 'King Arthur')
    >>> dot.node('B', 'Sir Bedevere the Wise')
    >>> dot.node('L', 'Sir Lancelot the Brave')

    >>> dot.edges(['AB', 'AL'])
    >>> dot.edge('B', 'L', constraint='false')

Check the generated source code:

.. code:: python

    >>> print(dot.source)  # doctest: +NORMALIZE_WHITESPACE
    // The Round Table
    digraph {
        A [label="King Arthur"]
        B [label="Sir Bedevere the Wise"]
        L [label="Sir Lancelot the Brave"]
            A -> B
            A -> L
            B -> L [constraint=false]
    }

Save and render the source code, optionally view the result:

.. code:: python

    >>> dot.render('test-output/round-table.gv', view=True)
    'test-output/round-table.gv.pdf'

.. image:: https://raw.github.com/xflr6/graphviz/master/docs/round-table.png
    :align: center


See also
--------

- pygraphviz_ |--| full-blown interface wrapping the Graphviz C library with SWIG
- graphviz-python_ |--| official Python bindings (documentation_)
- pydot_ |--| stable pure-Python approach, requires pyparsing


License
-------

This package is distributed under the `MIT license`_.


.. _pip: http://pip.readthedocs.org
.. _Graphviz:  http://www.graphviz.org
.. _download page: http://www.graphviz.org/Download.php
.. _DOT: http://www.graphviz.org/doc/info/lang.html

.. _pygraphviz: http://pypi.python.org/pypi/pygraphviz
.. _graphviz-python: https://pypi.python.org/pypi/graphviz-python
.. _documentation: http://www.graphviz.org/pdf/gv.3python.pdf
.. _pydot: http://pypi.python.org/pypi/pydot

.. _MIT license: http://opensource.org/licenses/MIT


.. |--| unicode:: U+2013


.. |PyPI version| image:: https://pypip.in/v/graphviz/badge.svg
    :target: https://pypi.python.org/pypi/graphviz
    :alt: Latest PyPI Version
.. |License| image:: https://pypip.in/license/graphviz/badge.svg
    :target: https://pypi.python.org/pypi/graphviz
    :alt: License
.. |Supported Python| image:: https://pypip.in/py_versions/graphviz/badge.svg
    :target: https://pypi.python.org/pypi/graphviz
    :alt: Supported Python Versions
.. |Format| image:: https://pypip.in/format/graphviz/badge.svg
    :target: https://pypi.python.org/pypi/graphviz
    :alt: Format
.. |Downloads| image:: https://pypip.in/d/graphviz/badge.svg
    :target: https://pypi.python.org/pypi/graphviz
    :alt: Downloads


