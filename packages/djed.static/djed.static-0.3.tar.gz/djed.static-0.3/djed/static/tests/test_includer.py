from pyramid.response import Response
from base import BaseTestCase


class TestIncluder(BaseTestCase):

    def test_components_includer(self):

        def view(request):
            request.include('anycomponent')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'djed.static:tests/bower_components')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/'
            b'anycomponent/1.0.0/anycomponent.js">'
            b'</script></head><body></body></html>'))

        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_custom_components_includer(self):

        def view(request):
            request.include('anycomponent', 'lib')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'djed.static:tests/bower_components', name='lib')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/lib/'
            b'anycomponent/1.0.0/anycomponent.js">'
            b'</script>'
            b'</head><body></body></html>'))

        response = app.get('/bowerstatic/lib/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_components_includer_in_template(self):

        def view(request):
            return {}

        self.config.include('pyramid_chameleon')
        self.config.add_route('view', '/')
        self.config.add_view(
            view, route_name='view',
            renderer='djed.static:tests/templates/index.pt')
        self.config.add_bower_components(
            'djed.static:tests/bower_components')

        app = self.make_app()
        response = app.get('/')

        self.assertIn(
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/'
            b'anycomponent/1.0.0/anycomponent.js">'
            b'</script>', response.body)

        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_components_includer_errors(self):
        from djed.static import Error

        self.assertRaises(Error, self.request.include, 'anycomponent')
        self.assertRaises(Error, self.request.include, 'not-exist-component')

    def test_local_components_includer(self):

        def view(request):
            request.include('myapp')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'djed.static:tests/bower_components', local=True)
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

    def test_local_components_includer_in_template(self):

        def view(request):
            return {}

        self.config.include('pyramid_chameleon')
        self.config.add_route('view', '/')
        self.config.add_view(
            view, route_name='view',
            renderer='djed.static:tests/templates/index_local.pt')
        self.config.add_bower_components(
            'djed.static:tests/bower_components', local=True)
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

    def test_custom_local_components_includer(self):

        def view(request):
            request.include('myapp', 'custom')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'djed.static:tests/bower_components',
            local=True, local_name='custom')
        self.config.add_bower_component(
            'djed.static:tests/local_component', '1.0.0', local_name='custom')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" src='
            b'"/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/custom/myapp/1.0.0/myapp.js"></script>'
            b'</head><body></body></html>'))

        response = app.get('/bowerstatic/custom/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')


    def test_custom_local_components_includer(self):

        def view(request):
            request.include('myapp', 'custom')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'djed.static:tests/bower_components',
            local=True, local_name='custom')
        self.config.add_bower_component(
            'djed.static:tests/local_component', '1.0.0', local_name='custom')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" src='
            b'"/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/custom/myapp/1.0.0/myapp.js"></script>'
            b'</head><body></body></html>'))

        response = app.get('/bowerstatic/custom/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')


    def test_custom_local_components_includer_in_custom_components(self):

        def view(request):
            request.include('myapp', 'custom')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'djed.static:tests/bower_components', name='lib',
            local=True, local_name='custom')
        self.config.add_bower_component(
            'djed.static:tests/local_component', '1.0.0', local_name='custom')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" src='
            b'"/bowerstatic/lib/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/custom/myapp/1.0.0/myapp.js"></script>'
            b'</head><body></body></html>'))

        response = app.get('/bowerstatic/custom/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')
