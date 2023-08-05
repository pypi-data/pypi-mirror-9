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


def init_bower_components(config, path):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    bower = get_bower(config.registry)
    components = bower.components(bower.components_name, directory)
    bower.local_components(bower.local_components_name, components)

    log.info("Initialize bower components: {0}".format(path))


def add_bower_component(config, path, version=None):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    bower = get_bower(config.registry)
    local = bower._component_collections.get(bower.local_components_name)
    if not local:
        raise Error("Bower components not initialized.")
    local.component(directory, version)

    log.info("Add local bower component: %s, version: %s" % (path, version))


def include(request, path_or_resource):
    bower = get_bower(request.registry)
    local = bower._component_collections.get(bower.local_components_name)
    if not local:
        raise Error("Bower components not initialized.")
    include = local.includer(request.environ)
    include(path_or_resource)


def includeme(config):
    bower = bower_factory_from_settings(config.registry.settings)
    config.registry.registerUtility(bower, IBower)

    config.add_tween('djed.static.bowerstatic_tween_factory')

    config.add_directive('init_bower_components', init_bower_components)
    config.add_directive('add_bower_component', add_bower_component)

    config.add_request_method(include, 'include')
    config.add_request_method(get_bower, 'get_bower')
