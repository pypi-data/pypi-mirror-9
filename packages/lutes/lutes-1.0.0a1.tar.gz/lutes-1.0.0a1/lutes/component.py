# -*- coding: utf-8 -*-
class Component:
    """A component is a data bag attached to an entity"""

    def __init__(self, entity=None):
        self.entity = entity
        """Entity the component relates to"""
