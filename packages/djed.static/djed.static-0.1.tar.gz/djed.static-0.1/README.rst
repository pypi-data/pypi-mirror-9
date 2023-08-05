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

Install the package into your python environment::

    pip install djed.static

Include it in your Pyramid application::

    config.include('djed.static')

Initialize it with a directory that contains the Bower packages::

    config.init_bower_components('myapp:static/bower_components')

If desired, add local Bower packages::

    config.add_bower_component('myapp:static/mycomponent')

Include required Bower packages on your page. You can do this in templates or
somewhere else in your code::

    request.include('bootstrap')

License
=======

djed.static is offered under the `ISC license`_.

.. _ISC license: http://choosealicense.com/licenses/isc/
