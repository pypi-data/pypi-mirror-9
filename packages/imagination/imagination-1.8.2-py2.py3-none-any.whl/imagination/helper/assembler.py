from re import split

from kotoba.kotoba import Kotoba
from kotoba        import load_from_file

from imagination.decorator.validator import restrict_type
from imagination.entity              import Entity
from imagination.exception           import *
from imagination.loader              import Loader
from imagination.helper.data         import *
from imagination.meta.aspect         import Contact
from imagination.meta.interception   import Interception
from imagination.meta.package        import Parameter
from imagination.proxy               import Proxy

class Assembler(object):
    """
    The entity assembler via configuration files.

    .. versionadded:: 1.5

    :param imagination.helper.data.Transformer transformer: the data transformer
    """
    __known_interceptable_events = ['before', 'pre', 'post', 'after']

    @restrict_type(Transformer)
    def __init__(self, transformer):
        self.__interceptions = []
        self.__transformer   = transformer
        self.__known_proxies = {}

    def activate_passive_loading(self):
        """ Activate the passive loading mode.

            This is to delay the instantiation or forking of an entity to when
            it is referred/queried but undefined. This assumes that the queried
            entity will later be defined.

            If later on it isn't defined, the exception will be thrown.

            When this method is used, please do not forget to call :meth:`deactivate_passive_loading`
            to disable the passive mode.

            .. versionadded:: 1.7
        """
        self.locator.in_passive_mode = True

    def deactivate_passive_loading(self):
        """ Deactivate the passive loading mode.

            When :meth:`activate_passive_loading` is used, this method must be
            called to disable the passive mode.

            .. versionadded:: 1.7
        """
        self.locator.in_passive_mode = False

    def load(self, filepath):
        """
        Load the configuration.

        :param str filepath: the file path to the configuration.
        """
        xml = load_from_file(filepath)

        # First, register proxies to entities (for lazy initialization).
        for node in xml.children():
            self.__validate_node(node)
            self.__register_proxy(node)

        # Then, register loaders for entities.
        for node in xml.children():
            self.__get_interceptions(node)
            self.__register_loader(node)

        # Then, declare interceptions to target entities.
        for interception in self.__interceptions:
            self.locator\
                .get_wrapper(interception.actor.id)\
                .register_interception(interception)

        self.__interceptions = []

    @property
    def locator(self):
        """
        The injected locator via the data transformer.

        :rtype: imagination.locator.Locator
        """
        return self.__transformer.locator()

    @restrict_type(Kotoba)
    def __validate_node(self, node):
        if not node.attribute('id'):
            raise IncompatibleBlockError('Invalid entity configuration. No ID specified.')

        if not node.attribute('class'):
            raise IncompatibleBlockError('Invalid entity configuration. No class type specified.')

    @restrict_type(Kotoba)
    def __register_proxy(self, node):
        id    = node.attribute('id')
        proxy = Proxy(self.locator, id)

        self.locator.set(id, proxy)

        # this is for interceptors
        self.__known_proxies[id] = proxy

    @restrict_type(Kotoba)
    def __register_loader(self, node):
        id     = node.attribute('id')
        kind   = node.attribute('class')
        params = self.__get_params(node)
        tags   = self.__get_tags(node)

        loader = Loader(kind)

        entity = Entity(id, loader, *params.largs, **params.kwargs)

        entity.interceptable = self.__transformer.cast(node.attribute('interceptable') or 'true', 'bool')
        entity.tags          = tags

        self.locator.set(id, entity)

    @restrict_type(Kotoba)
    def __get_tags(self, node):
        tags = node.attribute('tags')

        return tags and split(' ', tags.strip()) or []

    @restrict_type(Kotoba)
    def __get_interceptions(self, node):
        for sub_node in node.children('interception'):
            self.__interceptions.append(self.__get_interception(sub_node))

    @restrict_type(Kotoba)
    def __get_interception(self, node):
        actor = None
        event = None

        intercepted_action = None
        handling_action    = None

        for given_event in self.__known_interceptable_events:
            given_actor = node.attribute(given_event)

            # If the actor is not defined, continue or if the event is already
            # set (in the earlier iteration), raise the exception.
            if not given_actor:
                continue
            elif event:
                raise MultipleInterceptingEventsWarning(given_event)

            # Initially get the name of the actor and the handler.
            actor   = given_actor
            handler = node.parent().attribute('id')

            if actor == Interception.self_reference_keyword():
                actor = handler

            # If the actor or the handler has no proxies, raise the exception.
            if actor not in self.__known_proxies:
                raise UnknownProxyError('The target (%s) of the interception is unknown.' % actor)

            if handler not in self.__known_proxies:
                raise UnknownProxyError('The handler (%s) of the interception is unknown.' % handler)

            actor   = Contact(self.__known_proxies[actor], node.attribute('do'))
            handler = Contact(self.__known_proxies[handler], node.attribute('with'), self.__get_params(node))
            event   = given_event

        return Interception(event, actor, handler)

    @restrict_type(Kotoba)
    def __get_params(self, node):
        package = Parameter()

        index = 0

        for param in node.children('param'):
            try:
                assert param.attribute('name')\
                    and param.attribute('type'),\
                    'The parameter #%d does not have either name or type.' % index
            except AssertionError as e:
                raise IncompatibleBlockError(e.message)

            index += 1
            name   = param.attribute('name')

            if name in package.kwargs:
                raise DuplicateKeyWarning('There is a parameter name "%s" with that name already registered.' % name)
                pass

            package.kwargs[name] = self.__transformer.cast(
                param,
                param.attribute('type')
            )

        return package
