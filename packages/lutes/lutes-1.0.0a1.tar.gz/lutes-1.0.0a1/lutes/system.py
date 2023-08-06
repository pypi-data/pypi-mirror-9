# -*- coding: utf-8 -*-
class System:
    """A system handles a set of components.
    It is responsible for updating them.
    """

    def __init__(self, priority=99):
        self.priority = priority
        """System priority, lower is updated first"""
        self.manager = None
        self.entities = []
        """Entities handled by the system"""
        self.handled_components = []
        """Components the system needs to update entites"""

    def update(self, delta):
        """Update entities

        :param delta: time elapsed since last update
        """
        pass

    def init(self):
        """Initialize the system"""
        pass
