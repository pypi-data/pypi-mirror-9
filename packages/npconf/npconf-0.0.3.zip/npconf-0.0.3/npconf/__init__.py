# -*- coding: utf-8 -*-
"""
``npconf`` is a flexible configuration system whose configuration files are plain python modules. The identifiers
(left-hand side) are declared by the administrator/developer and are hierarchical. A typical configuration file might
be:

.. code-block:: python

    myapp.subcomponent.value = 1
    myapp.enabled = True

The user needn't define "myapp". It's automatically included in ``globals()``.

The administrator/developer can disallow user-defined attributes. This is mostly intended to prevent typos in the
configuration files. In other words, if ``myapp.foo`` is not defined before reading the configuration files, no file
will be allowed to set ``myapp.foo``.

The configuration attributes are normally declared by a program before it reads any configuration files. They can be
declared at init time:

.. code-block:: python

    import npconf

    root = npconf.ConfigValue(name='myapp', data={'enabled': 'false'})
    # and/or updated after init:
    root.update(data={'thing': None})

    # to add another level to the hierarchy:

    subcomponent = npconf.ConfigValue(
        name='subcomponent',
        data={
            'foo': 'banana',
    })
    root.update({'subcomponent': subcomponent})
"""
from main import *
