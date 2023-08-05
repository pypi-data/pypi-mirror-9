import logging
from zope.interface import Interface
from bowerstatic import (
    Bower,
    Error,
    InjectorTween,
    PublisherTween,
)
from pyramid.path import AssetResolver


log = logging.getLogger('djed.static')


class IBower(Interface):
    """ Bower interface
    """


def bower_factory_from_settings(settings):
    prefix = settings.get('djed.static.prefix', 'djed.static.')

    bower = Bower()

    bower.publisher_signature = settings.get(
        prefix + 'publisher_signature', 'bowerstatic')
    bower.components_name = settings.get(
        prefix + 'components_name', 'components')
    bower.local_components_name = settings.get(
        prefix + 'local_components_name', 'local')

    return bower


def get_bower(request):
    registry = getattr(request, 'registry', None)
    if registry is None:
        registry = request
    return registry.getUtility(IBower)


def bowerstatic_tween_factory(handler, registry):
    bower = get_bower(registry)

    def bowerstatic_tween(request):
        injector_handler = InjectorTween(bower, handler)
        publisher_handler = PublisherTween(bower, injector_handler)

        return publisher_handler(request)

    return bowerstatic_tween


def add_bower_components(config, path, name=None,
                         local=False, local_name=None):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    bower = get_bower(config.registry)

    if not name:
        name = bower.components_name

    components = bower.components(name, directory)

    if local:
        if not local_name:
            local_name = bower.local_components_name
        bower.local_components(local_name, components)

    log.info("Add bower components '{0}': {1}".format(name, path))


def add_bower_component(config, path, version=None, local_name=None):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    bower = get_bower(config.registry)

    if not local_name:
        local_name = bower.local_components_name

    local = bower._component_collections.get(local_name)

    if not local:
        raise Error("Bower local components not found.")

    local.component(directory, version)

    log.info("Add bower component: {0}".format(path))


def include(request, path_or_resource, components=None):
    bower = get_bower(request.registry)

    collection = bower._component_collections.get(components)

    if not collection:
        collection = bower._component_collections.get(
            bower.local_components_name)

    if not collection:
        collection = bower._component_collections.get(
            bower.components_name)

    if not collection:
        raise Error("Bower components not found.")

    include = collection.includer(request.environ)
    include(path_or_resource)


def includeme(config):
    bower = bower_factory_from_settings(config.registry.settings)
    config.registry.registerUtility(bower, IBower)

    config.add_tween('djed.static.bowerstatic_tween_factory')

    config.add_directive('add_bower_components', add_bower_components)
    config.add_directive('add_bower_component', add_bower_component)

    config.add_request_method(include, 'include')
    config.add_request_method(get_bower, 'get_bower')
