'''
:Author: Juti Noppornpitak

The module contains the entity locator used to promote reusability of components.

.. note::
    Copyright (c) 2012 Juti Noppornpitak

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
    of the Software, and to permit persons to whom the Software is furnished to do
    so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from re     import split
from kotoba import load_from_file

from imagination.entity    import CallbackProxy
from imagination.entity    import Entity
from imagination.exception import *
from imagination.proxy     import Proxy

class Locator(object):
    ''' Entity locator '''

    def __init__(self):
        self._entities          = {}
        self._tag_to_entity_ids = {}
        self._in_passive_mode   = False

    @property
    def in_passive_mode(self):
        return self._in_passive_mode

    @in_passive_mode.setter
    def in_passive_mode(self, value):
        if not isinstance(value, bool):
            raise ValueError('Expected a boolean value for in_passive_mode.')

        self._in_passive_mode = value

    def fork(self, id):
        '''
        Fork the entity identified by ``id``.

        :param `id`: entity identifier
        '''
        try:
            entity = self._entities[id]

            # Prevent the locator from forking a new instance of Proxy or CallbackProxy.
            if isinstance(entity, CallbackProxy) or isinstance(entity, Proxy):
                raise ForbiddenForkError('Unable to fork {}'.format(type(entity).__name__))

            return entity.fork()
        except KeyError:
            raise UnknownEntityError('The requested entity named "%s" is unknown or not found.' % id)

    @property
    def entity_identifiers(self):
        return self._entities.keys()

    def get(self, id):
        '''
        Retrieve an instance of the entity

        :param `id`: entity identifier
        :returns: an instance of the requested entity
        '''
        try:
            entity = self.get_wrapper(id)

            # Retrieve a callback entity (callable).
            if isinstance(entity, CallbackProxy):
                return entity()

            # Retrieve a proxy object to an entity
            if isinstance(entity, Proxy):
                return entity #return the proxy reference.

            return entity.instance if isinstance(entity, Entity) else entity
        except UnknownEntityError:
            raise UnknownEntityError(
                'The requested entity named "{id}" is unknown or not found. This locator only knows {known_keys}.'.format(
                    id=id,
                    known_keys=list(self._entities.keys())
                )
            )

    def get_wrapper(self, id):
        '''
        Retrieve the entity wrapper identified by ``id``.

        :param `id`: entity identifier
        :returns: the requested entity wrapper
        '''
        try:
            return self._entities[id]
        except KeyError:
            if self.in_passive_mode:
                return Proxy(self, id)

            raise UnknownEntityError('The requested entity named "%s" is unknown or not found.' % id)

    def find_by_tag(self, tag_label):
        '''
        Retrieve entities by *tag_label*.

        :param `tag_label`: tag label
        '''

        # First, get the entity identifiers.
        if tag_label not in self._tag_to_entity_ids:
            return []

        # Then, get references to entities.
        return [self.get(entity_id) for entity_id in self._tag_to_entity_ids[tag_label]]

    def has(self, id):
        return id in self._entities

    def set(self, id, entity):
        ''' Set the given *entity* by *id*. '''

        if type(entity) not in [Entity, Proxy, CallbackProxy]:
            raise UnknownEntityError('The type of the given entity named "{}" is not excepted. ({})'.format(id, type(entity).__name__))

        if isinstance(entity, Entity):
            entity.lock()

        self._entities[id] = entity

        if isinstance(entity, Proxy) or isinstance(entity, CallbackProxy):
            return

        for tag in entity.tags:
            if tag not in self._tag_to_entity_ids:
                self._tag_to_entity_ids[tag] = []

            self._tag_to_entity_ids[tag].append(entity.id)

    def has(self, id):
        ''' Check if the entity with *id* is already registered. '''
        return id in self._entities

    def load_xml(self, file_path):
        '''
        Load the entities from a XML configuration file at *file_path*.

        :Status: Deprecated in 1.5

        '''
        raise DeprecatedAPI('Use imagination.helper.assembler.Assembler.load instead.')
