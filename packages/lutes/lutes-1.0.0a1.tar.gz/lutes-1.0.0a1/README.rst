Lutes
=====

Pronounced as the ancient French city "Lutèce", Lutes is a micro component
entity system engine.

Component Entity System
-----------------------

Component entity system architecture  is often used in game development.

It allows great flexibility by using composition over inheritence. It is based on three core elements:

Entity
    An entity is a mere ID that represent an object in our world
Component
    A component is a structure holding the object data for an aspect of the world.
    Several components can be associated to an entity.
System
    A system contain the logic for an aspect of the world

Lutes adds a fourth element: the manager. The manager is the glue that ties components, entities and systems together.

You can learn more on component entity system architecture on `this wiki <http://entity-systems.wikidot.com/>`_.

What lutes gives you
--------------------

In its current state, lutes gives you a simplistic structure with basic elements you can inherit from.

Lutes is an experiment but should be functionnal: please see how green are the badges below.

.. image:: https://travis-ci.org/greizgh/lutes.svg?branch=master
    :target: https://travis-ci.org/greizgh/lutes

.. image:: https://coveralls.io/repos/greizgh/lutes/badge.svg?branch=master
    :target: https://coveralls.io/r/greizgh/lutes?branch=master

.. image:: https://readthedocs.org/projects/lutes/badge/?version=latest
    :target: https://readthedocs.org/projects/lutes/?badge=latest
