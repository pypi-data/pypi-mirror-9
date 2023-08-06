try:
    # python 2.x
    from urllib import quote
except ImportError:
    # python 3.x
    from urllib.parse import quote

import requests


def _quote(value):
    return quote(value, '')


class Client(object):
    """RabbitMQ Management plugin api

    Usage::

        >>> client = Client('http://localhost:15672', 'guest', 'guest')
        >>> client.get_vhosts()

    """
    def __init__(self, url, username, password):
        self._base_url = '{}/api'.format(url)
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._session.headers['content-type'] = 'application/json'

    def _build_url(self, args):
        args = map(_quote, args)
        return '{}/{}'.format(
            self._base_url,
            '/'.join(args),
        )

    def _request(self, method, *args, **kwargs):
        url = self._build_url(args)
        result = self._session.request(method, url, **kwargs)
        result.raise_for_status()
        if result.content:
            return result.json()


    def get_overview(self):
        """Various random bits of information that describe the whole
        system.

        """
        return self._request('GET', 'overview')

    def get_cluster_name(self):
        """Name identifying this RabbitMQ cluster.

        """
        return self._request('GET', 'cluster-name')

    def create_cluster_name(self):
        """Name identifying this RabbitMQ cluster.

        """
        return self._request('PUT', 'cluster-name')

    def get_nodes(self):
        """A list of nodes in the RabbitMQ cluster.

        """
        return self._request('GET', 'nodes')

    def get_nodes_by_name(self, name):
        """An individual node in the RabbitMQ cluster. Add "?memory=true"
        to get memory statistics, and "?binary=true" to get a breakdown
        of binary memory use (may be expensive if there are many small
        binaries in the system).

        :param str name:
        """
        return self._request('GET', 'nodes', name)

    def get_extensions(self):
        """A list of extensions to the management plugin.

        """
        return self._request('GET', 'extensions')

    def get_definitions(self):
        """The server definitions - exchanges, queues, bindings, users,
        virtual hosts, permissions and parameters. Everything apart from
        messages. POST to upload an existing set of definitions. Note
        that:

        + The definitions are merged. Anything already existing on the
          server but not in the uploaded definitions is untouched.

        """
        return self._request('GET', 'definitions')

    def get_connections(self):
        """A list of all open connections.

        """
        return self._request('GET', 'connections')

    def get_connections_by_name(self, name):
        """An individual connection. DELETEing it will close the
        connection. Optionally set the "X-Reason" header when DELETEing
        to provide a reason.

        :param str name:
        """
        return self._request('GET', 'connections', name)

    def delete_connections_by_name(self, name):
        """An individual connection. DELETEing it will close the
        connection. Optionally set the "X-Reason" header when DELETEing
        to provide a reason.

        :param str name:
        """
        return self._request('DELETE', 'connections', name)

    def get_connections_channels_by_name(self, name):
        """List of all channels for a given connection.

        :param str name:
        """
        return self._request('GET', 'connections', name, 'channels')

    def get_channels(self):
        """A list of all open channels.

        """
        return self._request('GET', 'channels')

    def get_channels_by_channel(self, channel):
        """Details about an individual channel.

        :param str channel:
        """
        return self._request('GET', 'channels', channel)

    def get_consumers(self):
        """A list of all consumers.

        """
        return self._request('GET', 'consumers')

    def get_consumers_by_vhost(self, vhost):
        """A list of all consumers in a given virtual host.

        :param str vhost:
        """
        return self._request('GET', 'consumers', vhost)

    def get_exchanges(self):
        """A list of all exchanges.

        """
        return self._request('GET', 'exchanges')

    def get_exchanges_by_vhost(self, vhost):
        """A list of all exchanges in a given virtual host.

        :param str vhost:
        """
        return self._request('GET', 'exchanges', vhost)

    def get_exchanges_by_vhost_and_name(self, vhost, name):
        """An individual exchange. To PUT an exchange, you will need a body
        looking something like this:

        ::

            {
                "auto_delete": False, 
                "internal": False, 
                "type": "direct", 
                "durable": True, 
                "arguments": {}
            }



        :param str vhost:
        :param str name:
        """
        return self._request('GET', 'exchanges', vhost, name)

    def create_exchanges_by_vhost_and_name(self, vhost, name):
        """An individual exchange. To PUT an exchange, you will need a body
        looking something like this:

        ::

            {
                "auto_delete": False, 
                "internal": False, 
                "type": "direct", 
                "durable": True, 
                "arguments": {}
            }



        :param str vhost:
        :param str name:
        """
        return self._request('PUT', 'exchanges', vhost, name)

    def delete_exchanges_by_vhost_and_name(self, vhost, name):
        """An individual exchange. To PUT an exchange, you will need a body
        looking something like this:

        ::

            {
                "auto_delete": False, 
                "internal": False, 
                "type": "direct", 
                "durable": True, 
                "arguments": {}
            }



        :param str vhost:
        :param str name:
        """
        return self._request('DELETE', 'exchanges', vhost, name)

    def get_exchanges_bindings_source_by_vhost_and_name(self, vhost, name):
        """A list of all bindings in which a given exchange is the source.

        :param str vhost:
        :param str name:
        """
        return self._request('GET', 'exchanges', vhost, name, 'bindings', 'source')

    def get_exchanges_bindings_destination_by_vhost_and_name(self, vhost, name):
        """A list of all bindings in which a given exchange is the
        destination.

        :param str vhost:
        :param str name:
        """
        return self._request('GET', 'exchanges', vhost, name, 'bindings', 'destination')

    def get_queues(self):
        """A list of all queues.

        """
        return self._request('GET', 'queues')

    def get_queues_by_vhost(self, vhost):
        """A list of all queues in a given virtual host.

        :param str vhost:
        """
        return self._request('GET', 'queues', vhost)

    def get_queues_by_vhost_and_name(self, vhost, name):
        """An individual queue. To PUT a queue, you will need a body
        looking something like this:

        ::

            {
                "node": "rabbit@smacmullen", 
                "auto_delete": False, 
                "durable": True, 
                "arguments": {}
            }



        :param str vhost:
        :param str name:
        """
        return self._request('GET', 'queues', vhost, name)

    def create_queues_by_vhost_and_name(self, vhost, name):
        """An individual queue. To PUT a queue, you will need a body
        looking something like this:

        ::

            {
                "node": "rabbit@smacmullen", 
                "auto_delete": False, 
                "durable": True, 
                "arguments": {}
            }



        :param str vhost:
        :param str name:
        """
        return self._request('PUT', 'queues', vhost, name)

    def delete_queues_by_vhost_and_name(self, vhost, name):
        """An individual queue. To PUT a queue, you will need a body
        looking something like this:

        ::

            {
                "node": "rabbit@smacmullen", 
                "auto_delete": False, 
                "durable": True, 
                "arguments": {}
            }



        :param str vhost:
        :param str name:
        """
        return self._request('DELETE', 'queues', vhost, name)

    def get_queues_bindings_by_vhost_and_name(self, vhost, name):
        """A list of all bindings on a given queue.

        :param str vhost:
        :param str name:
        """
        return self._request('GET', 'queues', vhost, name, 'bindings')

    def delete_queues_contents_by_vhost_and_name(self, vhost, name):
        """Contents of a queue. DELETE to purge. Note you can't GET this.

        :param str vhost:
        :param str name:
        """
        return self._request('DELETE', 'queues', vhost, name, 'contents')

    def get_bindings(self):
        """A list of all bindings.

        """
        return self._request('GET', 'bindings')

    def get_bindings_by_vhost(self, vhost):
        """A list of all bindings in a given virtual host.

        :param str vhost:
        """
        return self._request('GET', 'bindings', vhost)

    def get_bindings_by_vhost_and_exchange_and_queue(self, vhost, exchange, queue):
        """A list of all bindings between an exchange and a queue.
        Remember, an exchange and a queue can be bound together many
        times! To create a new binding, POST to this URI. You will need
        a body looking something like this:

        ::

            {
                "routing_key": "my_routing_key", 
                "arguments": {}
            }



        :param str vhost:
        :param str exchange:
        :param str queue:
        """
        return self._request('GET', 'bindings', vhost, 'e', exchange, 'q', queue)

    def get_bindings_by_vhost_and_exchange_and_queue_and_props(self, vhost, exchange, queue, props):
        """An individual binding between an exchange and a queue. The props

        :param str vhost:
        :param str exchange:
        :param str queue:
        :param str props:
        """
        return self._request('GET', 'bindings', vhost, 'e', exchange, 'q', queue, props)

    def delete_bindings_by_vhost_and_exchange_and_queue_and_props(self, vhost, exchange, queue, props):
        """An individual binding between an exchange and a queue. The props

        :param str vhost:
        :param str exchange:
        :param str queue:
        :param str props:
        """
        return self._request('DELETE', 'bindings', vhost, 'e', exchange, 'q', queue, props)

    def get_bindings_by_vhost_and_source_and_destination(self, vhost, source, destination):
        """A list of all bindings between two exchanges. Similar to the
        list of all bindings between an exchange and a queue, above.

        :param str vhost:
        :param str source:
        :param str destination:
        """
        return self._request('GET', 'bindings', vhost, 'e', source, 'e', destination)

    def get_bindings_by_vhost_and_source_and_destination_and_props(self, vhost, source, destination, props):
        """An individual binding between two exchanges. Similar to the
        individual binding between an exchange and a queue, above.

        :param str vhost:
        :param str source:
        :param str destination:
        :param str props:
        """
        return self._request('GET', 'bindings', vhost, 'e', source, 'e', destination, props)

    def delete_bindings_by_vhost_and_source_and_destination_and_props(self, vhost, source, destination, props):
        """An individual binding between two exchanges. Similar to the
        individual binding between an exchange and a queue, above.

        :param str vhost:
        :param str source:
        :param str destination:
        :param str props:
        """
        return self._request('DELETE', 'bindings', vhost, 'e', source, 'e', destination, props)

    def get_vhosts(self):
        """A list of all vhosts.

        """
        return self._request('GET', 'vhosts')

    def get_vhosts_by_name(self, name):
        """An individual virtual host. As a virtual host usually only has a
        name, you do not need an HTTP body when PUTing one of these. To
        enable / disable tracing, provide a body looking like:

        ::

            {
                "tracing": True
            }



        :param str name:
        """
        return self._request('GET', 'vhosts', name)

    def create_vhosts_by_name(self, name):
        """An individual virtual host. As a virtual host usually only has a
        name, you do not need an HTTP body when PUTing one of these. To
        enable / disable tracing, provide a body looking like:

        ::

            {
                "tracing": True
            }



        :param str name:
        """
        return self._request('PUT', 'vhosts', name)

    def delete_vhosts_by_name(self, name):
        """An individual virtual host. As a virtual host usually only has a
        name, you do not need an HTTP body when PUTing one of these. To
        enable / disable tracing, provide a body looking like:

        ::

            {
                "tracing": True
            }



        :param str name:
        """
        return self._request('DELETE', 'vhosts', name)

    def get_vhosts_permissions_by_name(self, name):
        """A list of all permissions for a given virtual host.

        :param str name:
        """
        return self._request('GET', 'vhosts', name, 'permissions')

    def get_users(self):
        """A list of all users.

        """
        return self._request('GET', 'users')

    def get_users_by_name(self, name):
        """An individual user. To PUT a user, you will need a body looking
        something like this:

        ::

            {
                "password": "secret", 
                "tags": "administrator"
            }



        :param str name:
        """
        return self._request('GET', 'users', name)

    def create_users_by_name(self, name):
        """An individual user. To PUT a user, you will need a body looking
        something like this:

        ::

            {
                "password": "secret", 
                "tags": "administrator"
            }



        :param str name:
        """
        return self._request('PUT', 'users', name)

    def delete_users_by_name(self, name):
        """An individual user. To PUT a user, you will need a body looking
        something like this:

        ::

            {
                "password": "secret", 
                "tags": "administrator"
            }



        :param str name:
        """
        return self._request('DELETE', 'users', name)

    def get_users_permissions_by_user(self, user):
        """A list of all permissions for a given user.

        :param str user:
        """
        return self._request('GET', 'users', user, 'permissions')

    def get_whoami(self):
        """Details of the currently authenticated user.

        """
        return self._request('GET', 'whoami')

    def get_permissions(self):
        """A list of all permissions for all users.

        """
        return self._request('GET', 'permissions')

    def get_permissions_by_vhost_and_user(self, vhost, user):
        """An individual permission of a user and virtual host. To PUT a
        permission, you will need a body looking something like this:

        ::

            {
                "write": ".*", 
                "read": ".*", 
                "configure": ".*"
            }



        :param str vhost:
        :param str user:
        """
        return self._request('GET', 'permissions', vhost, user)

    def create_permissions_by_vhost_and_user(self, vhost, user):
        """An individual permission of a user and virtual host. To PUT a
        permission, you will need a body looking something like this:

        ::

            {
                "write": ".*", 
                "read": ".*", 
                "configure": ".*"
            }



        :param str vhost:
        :param str user:
        """
        return self._request('PUT', 'permissions', vhost, user)

    def delete_permissions_by_vhost_and_user(self, vhost, user):
        """An individual permission of a user and virtual host. To PUT a
        permission, you will need a body looking something like this:

        ::

            {
                "write": ".*", 
                "read": ".*", 
                "configure": ".*"
            }



        :param str vhost:
        :param str user:
        """
        return self._request('DELETE', 'permissions', vhost, user)

    def get_parameters(self):
        """A list of all parameters.

        """
        return self._request('GET', 'parameters')

    def get_parameters_by_component(self, component):
        """A list of all parameters for a given component.

        :param str component:
        """
        return self._request('GET', 'parameters', component)

    def get_parameters_by_component_and_vhost(self, component, vhost):
        """A list of all parameters for a given component and virtual host.

        :param str component:
        :param str vhost:
        """
        return self._request('GET', 'parameters', component, vhost)

    def get_parameters_by_component_and_vhost_and_name(self, component, vhost, name):
        """An individual parameter. To PUT a parameter, you will need a
        body looking something like this:

        ::

            {
                "vhost": "/", 
                "component": "federation", 
                "name": "local_username", 
                "value": "guest"
            }



        :param str component:
        :param str vhost:
        :param str name:
        """
        return self._request('GET', 'parameters', component, vhost, name)

    def create_parameters_by_component_and_vhost_and_name(self, component, vhost, name):
        """An individual parameter. To PUT a parameter, you will need a
        body looking something like this:

        ::

            {
                "vhost": "/", 
                "component": "federation", 
                "name": "local_username", 
                "value": "guest"
            }



        :param str component:
        :param str vhost:
        :param str name:
        """
        return self._request('PUT', 'parameters', component, vhost, name)

    def delete_parameters_by_component_and_vhost_and_name(self, component, vhost, name):
        """An individual parameter. To PUT a parameter, you will need a
        body looking something like this:

        ::

            {
                "vhost": "/", 
                "component": "federation", 
                "name": "local_username", 
                "value": "guest"
            }



        :param str component:
        :param str vhost:
        :param str name:
        """
        return self._request('DELETE', 'parameters', component, vhost, name)

    def get_policies(self):
        """A list of all policies.

        """
        return self._request('GET', 'policies')

    def get_policies_by_vhost(self, vhost):
        """A list of all policies in a given virtual host.

        :param str vhost:
        """
        return self._request('GET', 'policies', vhost)

    def get_policies_by_vhost_and_name(self, vhost, name):
        """An individual policy. To PUT a policy, you will need a body
        looking something like this:

        ::

            {
                "priority": 0, 
                "pattern": "^amq.", 
                "apply-to": "all", 
                "definition": {
                    "federation-upstream-set": "all"
                }
            }



        :param str vhost:
        :param str name:
        """
        return self._request('GET', 'policies', vhost, name)

    def create_policies_by_vhost_and_name(self, vhost, name):
        """An individual policy. To PUT a policy, you will need a body
        looking something like this:

        ::

            {
                "priority": 0, 
                "pattern": "^amq.", 
                "apply-to": "all", 
                "definition": {
                    "federation-upstream-set": "all"
                }
            }



        :param str vhost:
        :param str name:
        """
        return self._request('PUT', 'policies', vhost, name)

    def delete_policies_by_vhost_and_name(self, vhost, name):
        """An individual policy. To PUT a policy, you will need a body
        looking something like this:

        ::

            {
                "priority": 0, 
                "pattern": "^amq.", 
                "apply-to": "all", 
                "definition": {
                    "federation-upstream-set": "all"
                }
            }



        :param str vhost:
        :param str name:
        """
        return self._request('DELETE', 'policies', vhost, name)

    def get_aliveness_test_by_vhost(self, vhost):
        """Declares a test queue, then publishes and consumes a message.
        Intended for use by monitoring tools. If everything is working
        correctly, will return HTTP status 200 with body:

        ::

            {
                "status": "ok"
            }



        :param str vhost:
        """
        return self._request('GET', 'aliveness-test', vhost)

