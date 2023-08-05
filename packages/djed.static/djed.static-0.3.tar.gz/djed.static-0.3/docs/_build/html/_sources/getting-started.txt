Getting Started
===============

Install the package into your python environment:

.. code-block:: sh

    $ /path/to/pyvenv/bin/pip install djed.static

Include it in your Pyramid application:

.. code-block:: python

    config.include('djed.static')

Add a ``bower_components`` directory:

.. code-block:: python

    config.add_bower_components('myapp:static/bower_components')

Include static resources on your HTML page. You can do this in templates or
somewhere else in your code:

.. code-block:: python

    request.include('bootstrap')

All additional required resources are automatically resolved and are also
included on your HTML page.
