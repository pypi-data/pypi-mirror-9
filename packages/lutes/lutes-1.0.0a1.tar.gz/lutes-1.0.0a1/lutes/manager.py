# -*- coding: utf-8 -*-
from .errors import InvalidEntityError


class Manager:
    """Manager handles entities and their components."""

    def __init__(self):
        self._index = 0
        self._components = {}
        self._entities = []
        self._systems = []
        self._subscribers = {}

    def create_entity(self):
        """Create an entity in the world and return its identifier.

        :rtype: entity
        """
        index = self._index
        self._entities.append(index)
        self._index += 1
        return index

    def remove_entity(self, entity):
        """Remove an entity from the world"""
        self._check_entity(entity)
        self._entities.remove(entity)
        for system in self._systems:
            if entity in system.entities:
                system.entities.remove(entity)
        for component_type in self._components:
            if entity in self._components[component_type]:
                # Related components should be orphans
                self._components[component_type][entity].entity = None
                del self._components[component_type][entity]

    def add_component(self, entity, component):
        """Add a component to an entity"""
        self._check_entity(entity)
        component.entity = entity
        if type(component) in self._components:
            if entity in self._components[type(component)]:
                # Old component is now orphan
                self._components[type(component)][entity].entity = None
            self._components[type(component)][entity] = component
        else:
            self._components[type(component)] = {entity: component}
        self._subscribe_entity(entity)

    def remove_component(self, entity, component):
        """Remove a component from an entity"""
        self._check_entity(entity)
        component.entity = None
        del self._components[component][entity]
        self._subscribe_entity(entity)

    def has_component(self, entity, component):
        """Check that given entity has component"""
        self._check_entity(entity)
        return entity in self._components[component]

    def get_component(self, entity, component):
        """Get an entity's component by its type
        Returns None if no component of given type was found

        :rtype: component or None
        """
        self._check_entity(entity)
        try:
            return self._components[component][entity]
        except KeyError:
            return None

    def add_system(self, system):
        """Add system to the world"""
        self._systems.append(system)
        system.manager = self
        self._systems.sort(key=lambda x: x.priority)

    def dispatch_event(self, event, data):
        """Dispatch an event to all subscribers

        :param event: event name as string
        :param data: data that will be passed to subscribers
        """
        if event in self._subscribers:
            for callback in self._subscribers[event]:
                callback(data)

    def subscribe(self, event, callback):
        """Subscribe a callback to an event

        :param event: event name as string
        :param callback: callable
        """
        if event in self._subscribers:
            self._subscribers[event].append(callback)
        else:
            self._subscribers[event] = [callback]

    def remove_system(self, system):
        """Remove a system from the world"""
        self._systems.remove(system)

    def update(self, delta):
        """Update every system

        :param delta: time elpased since last update
        """
        for system in self._systems:
            system.update(delta)

    def init(self):
        """Initialize systems"""
        for entity in self._entities:
            self._subscribe_entity(entity)
        for system in self._systems:
            system.init()

    def _subscribe_entity(self, entity):
        """Check if entity needs to be removed or added to a system"""
        for system in self._systems:
            if system.handled_components:
                matching_entity = True
                for component in system.handled_components:
                    if not self.has_component(entity, component):
                        matching_entity = False
                    if matching_entity and entity not in system.entities:
                        system.entities.append(entity)
                    elif not matching_entity and entity in system.entities:
                        system.entities.remove(entity)

    def _check_entity(self, entity):
        """Check that given entity is managed by the current instance"""
        if entity not in self._entities:
            raise InvalidEntityError(entity)
