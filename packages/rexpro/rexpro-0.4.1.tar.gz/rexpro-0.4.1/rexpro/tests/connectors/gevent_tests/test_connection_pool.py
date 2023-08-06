from unittest import TestCase
from rexpro._compat import PY2, xrange
from nose.plugins.attrib import attr
import os

if PY2:
    from rexpro.connectors.rgevent import RexProGeventConnectionPool, RexProGeventConnection

    import gevent

    @attr('pooling', 'gevent', 'python2')
    class TestGeventConnectionPooling(TestCase):

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

        test_slow_query(sleep_length, data)
        """

        def get_pool(self, host=None, port=None, graphname=None, graph_obj_name=None, username=None, password=None,
                     timeout=None):
            return RexProGeventConnectionPool(
                host=host or self.host,
                port=port or self.port,
                graph_name=graphname or self.default_graphname,
                graph_obj_name=graph_obj_name or self.default_graph_obj_name,
                username=username or self.username,
                password=password or self.password,
                timeout=timeout or self.timeout
            )

        def slow_start_simulation(self, pool):
            gevent.sleep(1)
            conn = pool.create_connection()
            return conn

        def spawn_slow_network_and_query_slow_response(self, pool, script, sleep_time, data):
            conn = self.slow_start_simulation(pool)
            conn.open_transaction()
            gevent.sleep(0)
            results = conn.execute(script=script, params={'sleep_length': sleep_time, 'data': data})
            gevent.sleep(0)
            conn.close_transaction()
            return results

        def test_pool_instantiation(self):
            pool = self.get_pool()

        def test_pool_returns_connection(self):
            pool = self.get_pool()
            conn = pool.create_connection()
            self.assertIsInstance(conn, RexProGeventConnection)
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
            gevent.joinall([
                gevent.spawn(pool.create_connection) for _ in xrange(self.NUM_ITER)
            ])

        def test_unique_connections(self):
            pool = self.get_pool()
            threads = []
            for i in xrange(self.NUM_ITER):
                threads.append(
                    gevent.spawn(self.spawn_slow_network_and_query_slow_response,
                                 pool, self.SLOW_NETWORK_QUERY, 1, {'value': i, i: 'value'})
                )

            gevent.joinall(threads, timeout=5)

        def test_context_manager(self):
            pool = self.get_pool()
            with pool.connection() as conn:
                results = conn.execute(script='values', params={'values': 5})
            self.assertEqual(results, 5)
