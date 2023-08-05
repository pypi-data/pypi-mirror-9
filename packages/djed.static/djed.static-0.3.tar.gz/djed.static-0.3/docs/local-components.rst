Local Components
================

If you develop your own front-end-code (so called "local components"), you
can also publish them with BowerStatic.

First of all you have to create a ``bower_components`` directory for
your local components:

.. code-block:: python

    config.add_bower_components('myapp:static/bower_components', local=True)

The ``local`` parameter indicates that the directory acts as fallback for
your local components. This means that the local components can use all the
available packages in the directory.

If you have created such a local ``bower_components`` directory, you can
add one or more local components:

.. code-block:: python

    config.add_bower_component('myapp:static/my_component', version='1.0.0')

You can retrieve the version of your Pyramid application like this:

.. code-block:: python

    import pkg_resources

    version = pkg_resources.get_distribution('myproject').version

Now you can include the added local components on your HTML page like any
other component:

.. code-block:: python

    request.include('my_component')

This includes your front-end-code in the HTML page and all dependencies that
are defined in the ``bower.json`` file.
