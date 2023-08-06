from unittest import TestCase
from rexpro._compat import PY2, xrange
from nose.plugins.attrib import attr
import os

if PY2:
    from rexpro.connectors.rgevent import RexProGeventConnection, RexProGeventSocket, RexProGeventConnectionPool
    import gevent

    def slow_start_simulation(ref):
        gevent.sleep(1)
        conn = ref.get_connection()
        return conn

    def spawn_slow_network_and_query_slow_response(ref, script, sleep_time, data):
        conn = slow_start_simulation(ref)
        return conn.execute(script=script, params={'sleep_length': sleep_time, 'data': data})

    @attr('concurrency', 'gevent', 'python2')
    class TestGeventConcurrency(TestCase):

        SOCKET_CLASS = RexProGeventSocket
        CONN_CLASS = RexProGeventConnection
        POOL_CLASS = RexProGeventConnectionPool

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

            gevent.joinall([gevent.spawn(self.get_connection) for _ in xrange(self.NUM_ITER)], timeout=3)

        def test_start_many_slow_connections(self):
            """ Test starting many slow connections """

            gevent.joinall([gevent.spawn(slow_start_simulation, self) for _ in xrange(self.NUM_ITER)], timeout=3)

        def test_many_network_calls(self):
            """ Test known responses on a network that should be slow, we should get them all asynchronously """

            threads = []

            for i in xrange(self.NUM_ITER):
                threads.append(gevent.spawn(spawn_slow_network_and_query_slow_response,
                                            self,
                                            self.SLOW_NETWORK_QUERY,
                                            1,
                                            {'value': i, i: 'value'}
                                            )
                               )

            gevent.joinall(threads, timeout=5)
