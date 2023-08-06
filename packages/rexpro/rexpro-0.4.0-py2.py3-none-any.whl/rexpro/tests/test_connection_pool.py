from unittest import TestCase
from nose.plugins.attrib import attr
from nose.tools import nottest
import os

from rexpro.connectors.sync import RexProSyncConnectionPool, RexProSyncConnection
from rexpro._compat import print_, xrange

import eventlet


@attr('unit', 'pooling')
class TestConnectionPooling(TestCase):

    host = os.getenv('TITAN_HOST', 'localhost')
    port = int(os.getenv('TITAN_REXPRO_PORT', 8184))
    default_graphname = 'emptygraph'
    default_graph_obj_name = 'g'
    username = 'rexster'
    password = 'rexster'
    timeout = 30

    NUM_ITER = 10
    SLOW_NETWORK_QUERY = """def test_slow_query(sleep_length, data) {
    sleep sleep_length
    return data
    }
    """

    def get_pool(self, host=None, port=None, graphname=None, graph_obj_name=None, username=None, password=None,
                 timeout=None):
        return RexProSyncConnectionPool(
            host=host or self.host,
            port=port or self.port,
            graph_name=graphname or self.default_graphname,
            graph_obj_name=graph_obj_name or self.default_graph_obj_name,
            username=username or self.username,
            password=password or self.password,
            timeout=timeout or self.timeout
        )

    def slow_start_simulation(self, pool):
        eventlet.sleep(1)
        conn = pool.create_connection()
        return conn

    def spawn_slow_network_and_query_slow_response(self, pool, script, sleep_time, data):
        conn = self.slow_start_simulation(pool)
        conn.open_transaction()
        eventlet.sleep(0)
        results = conn.execute(script=script, params={'sleep_length': sleep_time, 'data': data})
        eventlet.sleep(0)
        conn.close_transaction()
        return results

    def test_pool_instantiation(self):
        pool = self.get_pool()

    def test_pool_returns_connection(self):
        pool = self.get_pool()
        conn = pool.create_connection()
        self.assertIsInstance(conn, RexProSyncConnection)
        pool.close_connection(conn)

    def test_pool_returns_unique_connections(self):
        pool = self.get_pool()
        conn1 = pool.create_connection()
        conn2 = pool.create_connection()
        self.assertNotEqual(conn1, conn2)
        params1 = {'values': 1}
        params2 = {'values': 2}
        result1 = conn1.execute(script='values', params=params1)
        result2 = conn2.execute(script='values', params=params2)
        self.assertNotEqual(result1, result2)
        self.assertEqual(result1, 1)
        self.assertEqual(result2, 2)

    def test_many_concurrent_connections(self):
        pool = self.get_pool()
        epool = eventlet.GreenPool()
        for _ in xrange(self.NUM_ITER):
            epool.spawn_n(pool.create_connection)
        epool.waitall()

    def test_unique_connections(self):
        pool = self.get_pool()
        epool = eventlet.GreenPool()
        for i in xrange(self.NUM_ITER):
            epool.spawn_n(self.spawn_slow_network_and_query_slow_response,
                          pool, self.SLOW_NETWORK_QUERY, 1, {'value': i, i: 'value'})

        epool.waitall()

    def test_context_manager(self):
        pool = self.get_pool()
        with pool.connection() as conn:
            results = conn.execute(script='values', params={'values': 5})
        self.assertEqual(results, 5)
