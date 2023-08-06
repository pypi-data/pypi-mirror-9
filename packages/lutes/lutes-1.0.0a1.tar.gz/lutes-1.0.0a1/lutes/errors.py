# -*- coding: utf-8 -*-


class LutesError(Exception):
    """Root lutes exception, use it to catch lutes related exceptions"""
    pass


class InvalidEntityError(LutesError):
    """Exception raised when trying to process an invalid entity"""

    def __init__(self, entity):
        """
        :param entity: requested entity
        """
        self.entity = entity

    def __str__(self):
        return repr(self.entity)
