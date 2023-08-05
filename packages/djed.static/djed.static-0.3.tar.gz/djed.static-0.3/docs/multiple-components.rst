Multiple Component Directories
===============================

BowerStatic provides the possibility to create more than one
``bower_components`` directory. Each directory is an "isolated universe" of
components. Components in a ``bower_components`` directory can depend on each
other only – they cannot depend on components in another directory.

To add multiple ``bower_components`` directories, you need to give them
names:

.. code-block:: python

    config.add_bower_components('myapp:static/this_components', name='this')
    config.add_bower_components('myapp:static/that_components', name='that')

You can use components from this directories as follows:

.. code-block:: python

    request.include('jquery', 'this')
    request.include('bootstrap', 'that')

Several local components are also supported when you need it. Create some
local ``bower_components`` directories:

.. code-block:: python

    config.add_bower_components('myapp:static/this_components', name='this',
                                local=True, local_name='this_local')
    config.add_bower_components('myapp:static/that_components', name='that'
                                local=True, local_name='that_local')

Then you can add local components to them:

.. code-block:: python

    config.add_bower_component('myapp:static/some_component', verions='1.0.0',
                               local_name='this_local')
    config.add_bower_component('myapp:static/another_component', verions='1.0.0',
                               local_name='that_local')

After that, you can include your local components on the HTML page:

.. code-block:: python

    request.include('some_component', 'this_local')
    request.include('another_component', 'that_local')


