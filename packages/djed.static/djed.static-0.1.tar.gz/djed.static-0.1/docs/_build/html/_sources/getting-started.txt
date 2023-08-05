Getting Started
===============

Install the package into your python environment::

    pip install djed.static

Include it in your Pyramid application::

    config.include('djed.static')

Initialize a ``bower_components`` directory::

    config.init_bower_components('myapp:static/bower_components')

Include desired Bower packages on your page. You can do this in templates or
somewhere else in your code::

    request.include('bootstrap')

All required dependencies are also included on the page.
