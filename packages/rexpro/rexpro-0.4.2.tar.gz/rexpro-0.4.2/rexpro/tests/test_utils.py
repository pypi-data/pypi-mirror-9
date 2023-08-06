from unittest import TestCase
from rexpro._compat import PY2
from nose.plugins.attrib import attr
from rexpro.utils import get_rexpro
from rexpro.exceptions import RexProInvalidConnectorTypeException
from rexpro.connectors.sync import RexProSyncSocket, RexProSyncConnection, RexProSyncConnectionPool
if PY2:
    from rexpro.connectors.rgevent import RexProGeventSocket, RexProGeventConnection, RexProGeventConnectionPool
from rexpro.connectors.reventlet import RexProEventletSocket, RexProEventletConnection, RexProEventletConnectionPool


@attr('unit', 'utils')
class TestRexProUtils(TestCase):

    def test_retrieve_defaults(self):
        """ Test retreive default classes (Sync) """
        sock, conn, pool = get_rexpro()
        self.assertTrue(issubclass(sock, RexProSyncSocket))
        self.assertTrue(issubclass(conn, RexProSyncConnection))
        self.assertTrue(issubclass(pool, RexProSyncConnectionPool))

        sock, conn, pool = get_rexpro(None)
        self.assertTrue(issubclass(sock, RexProSyncSocket))
        self.assertTrue(issubclass(conn, RexProSyncConnection))
        self.assertTrue(issubclass(pool, RexProSyncConnectionPool))

    def test_raise_invalid_type(self):
        with self.assertRaises(RexProInvalidConnectorTypeException):
            sock, conn, pool = get_rexpro('doesnotexist')

    def test_get_sync(self):
        """ Test retrieve sync classes """
        sock, conn, pool = get_rexpro('sync')
        self.assertTrue(issubclass(sock, RexProSyncSocket))
        self.assertTrue(issubclass(conn, RexProSyncConnection))
        self.assertTrue(issubclass(pool, RexProSyncConnectionPool))

        sock, conn, pool = get_rexpro(u'sync')
        self.assertTrue(issubclass(sock, RexProSyncSocket))
        self.assertTrue(issubclass(conn, RexProSyncConnection))
        self.assertTrue(issubclass(pool, RexProSyncConnectionPool))

    def test_get_gevent(self):
        """ Test retrieve gevent classes """
        if PY2:
            sock, conn, pool = get_rexpro('gevent')
            self.assertTrue(issubclass(sock, RexProGeventSocket))
            self.assertTrue(issubclass(conn, RexProGeventConnection))
            self.assertTrue(issubclass(pool, RexProGeventConnectionPool))

    def test_get_eventlet(self):
        """ Test retrieve eventlet classes """
        sock, conn, pool = get_rexpro('eventlet')
        self.assertTrue(issubclass(sock, RexProEventletSocket))
        self.assertTrue(issubclass(conn, RexProEventletConnection))
        self.assertTrue(issubclass(pool, RexProEventletConnectionPool))