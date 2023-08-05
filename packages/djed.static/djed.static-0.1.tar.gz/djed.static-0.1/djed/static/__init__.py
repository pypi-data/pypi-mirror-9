import logging
from bowerstatic import (
    Bower,
    Error,
    InjectorTween,
    PublisherTween,
)
from pyramid.path import AssetResolver


log = logging.getLogger('djed.static')


class bowerstatic_tween_factory(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        injector_handler = InjectorTween(
            self.registry.bower,
            self.handler)
        publisher_handler = PublisherTween(
            self.registry.bower,
            injector_handler)

        return publisher_handler(request)


def init_bower_components(config, path):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()
    components = config.registry.bower.components('components', directory)
    local = config.registry.bower.local_components('local', components)

    log.info("Initialize static components: {0}".format(path))


def add_bower_component(config, path, version=None):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()
    local = config.registry.bower._component_collections.get('local')
    if not local:
        raise Error("Static components not initialized.")
    local.component(directory, version)

    log.info("Add local static component: %s, version: %s" % (path, version))


def include(request, path_or_resource):
    local = request.registry.bower._component_collections.get('local')
    if not local:
        raise Error("Static components not initialized.")
    include = local.includer(request.environ)
    include(path_or_resource)


def includeme(config):
    config.registry.bower = Bower()

    config.add_tween('djed.static.bowerstatic_tween_factory')
    config.add_directive('init_bower_components', init_bower_components)
    config.add_directive('add_bower_component', add_bower_component)
    config.add_request_method(include, 'include')
