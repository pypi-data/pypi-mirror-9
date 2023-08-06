Rabbitman
=========

Python client for the `RabbitMQ management plugin
<https://www.rabbitmq.com/management.html>`_.

::

    >>> from rabbitman import Client
    >>> client = Client('http://localhost:15672', 'guest', 'guest')
    >>> client.get_vhosts()
    [{
        'name': '/',
        'messages': 48,
        'tracing': False,
        # ...
    },
    # ...
    ]


Installing
----------

::

    pip install rabbitman


Why not pyrabbit
----------------

The code for this client is auto-generated from the api documentation, and so
has complete support for all endpoints. We are also based on `requests` instead
of `httplib2`, which in our experience is more stable.



License
-------

This package is licensed under MIT. The api enpoint documentation is generated
from documentation at
`https://www.rabbitmq.com/management.html
<https://github.com/rabbitmq/rabbitmq-management/blob/master/LICENSE-MPL-RabbitMQ>`_,
licensed under the MPL.
