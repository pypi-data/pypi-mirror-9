from pyramid.response import Response
from base import BaseTestCase


class TestSettings(BaseTestCase):

    def test_default(self):
        request = self.make_request()
        bower = request.get_bower()

        self.assertEqual(bower.publisher_signature, 'bowerstatic')
        self.assertEqual(bower.components_name, 'components')
        self.assertEqual(bower.local_components_name, 'local')


class TestSettingsCustom(BaseTestCase):

    _settings = {
        'djed.static.publisher_signature': 'static',
        'djed.static.components_name': 'lib',
        'djed.static.local_components_name': 'app',
    }

    def test_custom(self):
        request = self.make_request()
        bower = request.get_bower()

        self.assertEqual(bower.publisher_signature, 'static')
        self.assertEqual(bower.components_name, 'lib')
        self.assertEqual(bower.local_components_name, 'app')

    def test_include_path(self):

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
            b'"/static/lib/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/static/app/myapp/1.0.0/myapp.js"></script>'
            b'</head><body></body></html>'))
