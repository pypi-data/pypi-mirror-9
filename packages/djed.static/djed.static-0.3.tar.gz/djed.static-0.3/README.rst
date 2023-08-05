===========
djed.static
===========

.. image:: https://travis-ci.org/djedproject/djed.static.png?branch=master
   :target: https://travis-ci.org/djedproject/djed.static

djed.static integrates BowerStatic_ into the `Pyramid Web Framework`_.
BowerStatic is a WSGI component that can serve static resources from
front-end packages (JavaScript, CSS) that you install through the Bower_
package manager.

.. _Bower: http://bower.io

.. _BowerStatic: https://bowerstatic.readthedocs.org

.. _Pyramid Web Framework: https://pyramid.readthedocs.org

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

Documentation and Support
=========================

Documentation can be found at `http://djedstatic.readthedocs.org/  <https://djedstatic.readthedocs.org/>`_

If you've got questions, contact the `djedproject mailling list <https://groups.google.com/group/djedproject>`_.

To report bugs, use the `issue tracker <https://github.com/djedproject/djed.static/issues>`_.

License
=======

djed.static is offered under the `ISC license`_.

.. _ISC license: http://choosealicense.com/licenses/isc/
