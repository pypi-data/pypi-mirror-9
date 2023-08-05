from webtest import TestApp
from pyramid.response import Response
from base import BaseTestCase


class TestStaticConfig(BaseTestCase):

    _includes = ()

    def test_include(self):
        request = self.make_request()

        self.assertFalse(hasattr(self.config, 'init_bower_components'))
        self.assertFalse(hasattr(self.config, 'add_bower_component'))
        self.assertFalse(hasattr(request, 'include'))

        self.config.include('djed.static')
        request = self.make_request()

        self.assertTrue(hasattr(self.config, 'init_bower_components'))
        self.assertTrue(hasattr(self.config, 'add_bower_component'))
        self.assertTrue(hasattr(request, 'include'))


class TestStatic(BaseTestCase):

    def test_init(self):

        self.config.init_bower_components(
            'djed.static:tests/bower_components')

        self.assertIn('components',
                      self.config.registry.bower._component_collections)
        self.assertIn('local',
                      self.config.registry.bower._component_collections)

    def test_add_local_component(self):

        self.config.init_bower_components(
            'djed.static:tests/bower_components')
        self.config.add_bower_component(
            'djed.static:tests/local_component')

        local = self.config.registry.bower._component_collections['local']

        self.assertIn('myapp', local._components)

    def test_init_errors(self):
        from djed.static import Error

        self.assertRaises(Error, self.config.add_bower_component,
                          'djed.static:tests/local_component')

        self.assertRaises(Error, self.request.include, 'anycomponent')

    def test_request_include(self):

        def view(request):
            request.include('anycomponent')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.init_bower_components(
            'djed.static:tests/bower_components')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script></head><body></body></html>'))

        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_request_include_in_template(self):

        def view(request):
            return {}

        self.config.include('pyramid_chameleon')
        self.config.add_route('view', '/')
        self.config.add_view(
            view, route_name='view',
            renderer='djed.static:tests/templates/index.pt')
        self.config.init_bower_components(
            'djed.static:tests/bower_components')

        app = self.make_app()
        response = app.get('/')

        self.assertIn(
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script>', response.body)

        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_request_include_error(self):
        from djed.static import Error

        self.config.init_bower_components(
            'djed.static:tests/bower_components')

        self.assertRaises(Error, self.request.include, 'anotherComponent')

    def test_request_include_local_component(self):

        def view(request):
            request.include('myapp')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.init_bower_components(
            'djed.static:tests/bower_components')
        self.config.add_bower_component(
            'djed.static:tests/local_component', '1.0.0')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" src='
            b'"/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/local/myapp/1.0.0/myapp.js"></script>'
            b'</head><body></body></html>'))


        response = app.get('/bowerstatic/local/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')

    def test_request_include_local_component_in_template(self):

        def view(request):
            return {}

        self.config.include('pyramid_chameleon')
        self.config.add_route('view', '/')
        self.config.add_view(
            view, route_name='view',
            renderer='djed.static:tests/templates/index_local.pt')
        self.config.init_bower_components(
            'djed.static:tests/bower_components')
        self.config.add_bower_component(
            'djed.static:tests/local_component', '1.0.0')

        app = self.make_app()
        response = app.get('/')

        self.assertIn((
            b'<script type="text/javascript" src='
            b'"/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/local/myapp/1.0.0/myapp.js"></script>'),
            response.body)


        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

        response = app.get('/bowerstatic/local/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')
