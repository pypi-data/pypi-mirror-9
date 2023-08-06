from unittest import TestCase
from rexpro._compat import print_, xrange
from nose.plugins.attrib import attr
import os

from rexpro.connectors.reventlet import RexProEventletConnection, RexProEventletConnectionPool, RexProEventletSocket

import eventlet


def slow_start_simulation(ref):
    eventlet.sleep(1)
    conn = ref.get_connection()
    return conn


def spawn_slow_network_and_query_slow_response(ref, script, sleep_time, data):
    conn = slow_start_simulation(ref)
    return conn.execute(script=script, params={'sleep_length': sleep_time, 'data': data})


@attr('concurrency', 'eventlet')
class TestEventletConcurrency(TestCase):

    SOCKET_CLASS = RexProEventletSocket
    CONN_CLASS = RexProEventletConnection
    POOL_CLASS = RexProEventletConnectionPool

    host = os.getenv('TITAN_HOST', 'localhost')
    port = int(os.getenv('TITAN_REXPRO_PORT', 8184))
    default_graphname = 'emptygraph'
    username = 'rexster'
    password = 'rexster'
    timeout = 30

    test_graphs = [
        'emptygraph',  # Tinkergraph
        'graph',  # Tinkergraph
        #'emptysailgraph',  # in memory sail graph
        #'sailgraph',  #sail graph
        #'orientdbsample',  # OrientDB
        #'neo4jsample',  # Neo4j
        #'dexsample',  # DexGraph
        #'titangraph',  # Titan
    ]

    NUM_ITER = 10
    SLOW_NETWORK_QUERY = """def test_slow_query(sleep_length, data) {
    sleep sleep_length
    return data
    }

    test_slow_query(sleep_length, data)
    """

    def get_connection(self, host=None, port=None, graphname=None, username=None, password=None, timeout=None):
        return self.CONN_CLASS(
            host or self.host,
            port or self.port,
            graphname or self.default_graphname,
            username=username or self.username,
            password=password or self.password,
            timeout=timeout or self.timeout
        )

    def test_start_many_connections(self):
        """ Test starting up many connections """

        pile = eventlet.GreenPile()
        [pile.spawn(self.get_connection)for _ in xrange(self.NUM_ITER)]
        for conn in pile:
            self.assertIsInstance(conn, RexProEventletConnection)

    def test_start_many_slow_connections(self):
        """ Test starting many slow connections """

        pile = eventlet.GreenPile()
        [pile.spawn(self.get_connection) for _ in xrange(self.NUM_ITER)]
        for conn in pile:
            self.assertIsInstance(conn, RexProEventletConnection)

    def test_many_network_calls(self):
        """ Test known responses on a network that should be slow, we should get them all asynchronously """

        pile = eventlet.GreenPile()

        for i in xrange(self.NUM_ITER):
            pile.spawn(spawn_slow_network_and_query_slow_response,
                       self,
                       self.SLOW_NETWORK_QUERY,
                       1,
                       {'value': i, i: 'value'}
                       )

        for result in pile:
            print_(result)
            self.assertIsInstance(result, dict)
