from rexpro._compat import PY2
if PY2:
    from .connection import RexProGeventSocket, RexProGeventConnectionPool, RexProGeventConnection
