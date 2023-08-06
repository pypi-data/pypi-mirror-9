from unittest import skip
from nose.plugins.attrib import attr
from mock import patch

from rexpro.tests.base import BaseRexProTestCase, multi_graph
from rexpro._compat import print_, string_types

from rexpro import exceptions


@attr('unit')
class TestConnection(BaseRexProTestCase):

    @attr('metrics-setup')
    def test_connection_success(self):
        """ Test Creating a connection """
        conn = self.get_connection()

    def test_attempting_to_connect_to_an_invalid_graphname_raises_exception(self):
        """ Attempting to connect to a nonexistant graph should raise a RexProConnectionException """
        with self.assertRaises(exceptions.RexProGraphConfigException):
            self.get_connection(graphname='nothing')

    def test_invalid_connection_info_raises_exception(self):
        """ Attempting to connect with invalid information should raise and Exception """
        with self.assertRaises(exceptions.RexProConnectionException):
            self.get_connection(host='1.2.3.4', timeout=0.1)

    def test_connection_close_prematurely(self):
        """ Attempting to send/recieve with premature connection close """
        conn = self.get_connection()
        conn._conn.close()
        with self.assertRaises(Exception):
            conn._conn.get_response()

    @skip
    def test_invalid_msgpack(self):
        """ Attempting to test invalid msgpack channel setup """
        conn = self.get_connection()
        with patch('rexpro.connection.socket') as mocket:
            mocket.recv.return_value = '\x00'
            # testing the msg_version
            with self.assertRaises(exceptions.RexProConnectionException):
                conn._conn.get_response()

            #testing the serializer type
            mocket.recv.return_value = '\x10'
            with self.assertRaises(exceptions.RexProConnectionException):
                conn._conn.get_response()

    @skip
    def test_call_close_transactions_without_an_open_transaction_fails(self):
        pass

    @skip
    def test_call_open_transaction_with_a_transaction_already_open_fails(self):
        pass


@attr('unit')
class TestQueries(BaseRexProTestCase):

    @multi_graph
    def test_data_integrity(self):
        """
        Tests that simply being passed through rexster comes unchanged
        """
        conn = self.get_connection(graphname=self.graphname)

        e = lambda p: conn.execute(
            script='values',
            params={'values': p}
        )

        #test string
        data = e('yea boyeeee')
        self.assertIsInstance(data, string_types)
        self.assertEqual(data, 'yea boyeeee')

        #test int
        data = e(1982)
        self.assertEqual(data, 1982)

        #test float
        data = e(3.14)
        self.assertEqual(data, 3.14)

        #test dict
        data = e({'blake': 'eggleston'})
        self.assertEqual(data, {'blake': 'eggleston'})

        #test none
        data = e(None)
        self.assertIsNone(data)

        #test list
        data = e([1, 2])
        self.assertEqual(data, [1, 2])

    def test_query_isolation(self):
        """ Test that variables defined in one query are not available in subsequent queries """
        conn = self.get_connection()

        conn.execute(
            """
            def one_val = 5
            one_val
            """,
        )

        with self.assertRaises(exceptions.RexProScriptException):
            r = conn.execute(
                """
                one_val
                """
            )

    def test_element_creation(self):
        """ Tests that vertices and edges can be created and are serialized properly """

        conn = self.get_connection()
        elements = conn.execute(
            """
            def v1 = g.addVertex([prop:6])
            def v2 = g.addVertex([prop:8])
            def e = g.addEdge(v1, v2, 'connects', [prop:10])
            return [v1, v2, e]
            """
        )
        v1, v2, e = elements
        self.assertEqual(v1['_properties']['prop'], 6)
        self.assertEqual(v2['_properties']['prop'], 8)
        self.assertEqual(e['_properties']['prop'], 10)

        self.assertEqual(e['_outV'], v1['_id'])
        self.assertEqual(e['_inV'], v2['_id'])


@attr('unit')
class TestTransactions(BaseRexProTestCase):

    def test_transaction_isolation(self):
        """ Tests that operations between 2 transactions are isolated """
        conn1 = self.get_connection()
        conn2 = self.get_connection()

        if conn1.graph_features['supportsTransactions']:

            with conn1.transaction():
                v1, v2, v3 = conn1.execute(
                    """
                    def v1 = g.addVertex([val:1, str:"vertex 1"])
                    def v2 = g.addVertex([val:2, str:"vertex 2"])
                    def v3 = g.addVertex([val:3, str:"vertex 3"])
                    [v1, v2, v3]
                    """
                )

            print_("{}, {}, {}".format(v1, v2, v3))

            conn1.open_transaction()
            conn2.open_transaction()

            v1_1 = conn1.execute(
                """
                def v1 = g.v(eid)
                v1.setProperty("str", "v1")
                v1
                """,
                params={'eid': v1['_id']}
            )

            v1_2 = conn2.execute(
                """
                g.v(eid)
                """,
                params={'eid': v1['_id']}
            )

            self.assertEqual(v1_2['_properties']['str'], 'vertex 1')

    def test_bad_multiple_transactions_one_connection(self):
        """ Tests that the transaction manager prevents more than one simultaneous transaction on a single connection
        """

        conn = self.get_connection()

        if conn.graph_features['supportsTransactions']:
            with conn.transaction():
                with self.assertRaises(exceptions.RexProException):
                    with conn.transaction():
                        pass

        conn.close()

    def test_bad_close_transaction(self):
        """ Tests that a transaction cannot be closed without at first having a transaction """
        conn = self.get_connection()

        with self.assertRaises(exceptions.RexProScriptException):
            conn.close_transaction()
