from rexpro.connectors import SUPPORTED_CONNECTORS
from rexpro.exceptions import RexProInvalidConnectorTypeException
from rexpro._compat import PY2
from rexpro.connectors.sync import RexProSyncSocket, RexProSyncConnection, RexProSyncConnectionPool
import sys


def get_rexpro(stype='sync'):
    """ Obtain the RexPro Socket, Connection and Connection Pool classes for the desired application

    Options include:
      - 'sync' - Default, Synchronous python sockets
      - 'gevent' - with gevent concurrency
      - 'eventlet' - with eventlet concurrency

    Example:

    .. code-block:: python

        from rexpro.utils import get_rexpro
        sock_cls, conn_cls, pool_cls = get_rexpro()            # Returns the Synchronous classes
        sock_cls, conn_cls, pool_cls = get_rexpro('sync')      # Returns the Synchronous classes
        sock_cls, conn_cls, pool_cls = get_rexpro('gevent')    # Returns the Gevent classes
        sock_cls, conn_cls, pool_cls = get_rexpro('eventlet')  # Returns the Eventlet classes

    """
    if stype is None:
        return RexProSyncSocket, RexProSyncConnection, RexProSyncConnectionPool
    if stype.lower() not in SUPPORTED_CONNECTORS:
        raise RexProInvalidConnectorTypeException("Not a supported connector type: {}".format(stype))
   
    def import_obj(import_string):
        module, obj = import_string.rsplit('.', 1)
         
        # Python2 is unable to handle unicode string imports
        if PY2 and isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        try:
            return getattr(__import__(module, None, None, [obj]), obj)
        except (ImportError, AttributeError):
            # support modules not yet import by their parent module or package
            modname = module + '.' + obj
            __import__(modname)
            return sys.modules[modname]

    return (import_obj(SUPPORTED_CONNECTORS[stype.lower()][0]),
            import_obj(SUPPORTED_CONNECTORS[stype.lower()][1]),
            import_obj(SUPPORTED_CONNECTORS[stype.lower()][2]))

