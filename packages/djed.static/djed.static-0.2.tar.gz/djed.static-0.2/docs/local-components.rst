Local Components
================

If you develop your own front-end-code (so called "local components"), you
can add them as follows::

    config.add_bower_component('myapp:static/my_component', version='1.0.0')

You can retrieve the version of your Pyramid application like this::

    import pkg_resources

    version = pkg_resources.get_distribution('myproject').version

You can include local components on page like any other component::

    request.include('my_component')

This includes your front-end-code on the page and all dependencies that are
defined in the ``bower.json`` file.
