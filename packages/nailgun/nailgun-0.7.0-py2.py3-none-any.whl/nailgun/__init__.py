# -*- coding: utf-8 -*-
"""The root of the NailGun namespace.

NailGun's modules are organized in to a tree of dependencies, where each module
only knows about the modules below it in the tree. (The ``nailgun.entities``
module is in the process of being ported over from robottelo.) They can be
visualized like this::

    nailgun.entities
    └── nailgun.entity_mixins
        ├── nailgun.entity_fields
        ├── nailgun.config
        └── nailgun.client

As an end user, you'll typically want to use the classes exposed by
``nailgun.entities``.

"""
