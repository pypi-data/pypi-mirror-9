from pyramid.response import Response
from base import BaseTestCase


class TestLocalComponents(BaseTestCase):

    def test_add_local_component(self):

        self.config.add_bower_components(
            'djed.static:tests/bower_components', local=True)
        self.config.add_bower_component(
            'djed.static:tests/local_component')

        bower = self.request.get_bower()

        self.assertIn('local', bower._component_collections)

        local = bower._component_collections['local']

        self.assertIn('myapp', local._components)

    def test_add_custom_local_component(self):

        self.config.add_bower_components(
            'djed.static:tests/bower_components',
            local=True, local_name='custom')
        self.config.add_bower_component(
            'djed.static:tests/local_component', local_name='custom')

        bower = self.request.get_bower()

        self.assertIn('custom', bower._component_collections)

        local = bower._component_collections['custom']

        self.assertIn('myapp', local._components)

    def test_add_custom_local_component_to_name_components(self):

        self.config.add_bower_components(
            'djed.static:tests/bower_components', name='lib',
            local=True, local_name='custom')
        self.config.add_bower_component(
            'djed.static:tests/local_component',
            local_name='custom')

        bower = self.request.get_bower()

        self.assertIn('custom', bower._component_collections)

        local = bower._component_collections['custom']

        self.assertIn('myapp', local._components)

    def test_add_local_component_error(self):
        from djed.static import Error

        self.assertRaises(Error, self.config.add_bower_component,
                          'djed.static:tests/local_component')

