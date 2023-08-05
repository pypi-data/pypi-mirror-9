codegrapher
===========

.. image:: https://travis-ci.org/LaurEars/codegrapher.svg?branch=master
    :target: https://travis-ci.org/LaurEars/codegrapher


Code that graphs code
---------------------
Uses the python `AST <https://docs.python.org/2/library/ast.html>`_ to parse Python source code and build a call graph.


Output
------
An example of the current output of the parser parsing itself.

.. image:: http://i.imgur.com/QMES0Na.png
    :target: http://i.imgur.com/QMES0Na.png
    :align: center
    :width: 100 %
    :alt: parser.py


Installation
------------

.. code:: bash

    pip install codegrapher


To generate graphs, `graphviz <http://www.graphviz.org/Download.php>`_ must be installed.


Usage
-----

At the command line
~~~~~~~~~~~~~~~~~~~
To parse a file and output results to the console:

.. code:: bash

    codegrapher path/to/file.py --printed


To parse a file and output results to a file:

.. code:: bash

    codegrapher path/to/file.py --output output_file_name --output-type png

To analyze a directory of files, along with all files it contains:

.. code:: bash

    codegrapher -r path/to/directory --output multiple_file_analysis


As a Python module
~~~~~~~~~~~~~~~~~~

To easily parse code in Python :

.. code:: python

    from codegrapher.parser import FileObject

    file_object = FileObject('path/to/file.py')
    file_object.visit()

And then to add that code to a graph and render it (using graphviz):

.. code:: python

    from codegrapher.graph import FunctionGrapher

    graph = FunctionGrapher()
    graph.add_file_to_graph(file_object)
    graph.name = 'name.gv'
    graph.format = 'png'
    graph.render()

Which will produce your code as a png file, `name.gv.png`, along with a
`dot file <http://en.wikipedia.org/wiki/DOT_%28graph_description_language%29>`_ `name.gv`