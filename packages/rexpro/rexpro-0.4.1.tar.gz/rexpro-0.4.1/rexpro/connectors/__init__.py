# supported connection types
SUPPORTED_CONNECTORS = {
    'sync': ('rexpro.connectors.sync.RexProSyncSocket',
             'rexpro.connectors.sync.RexProSyncConnection',
             'rexpro.connectors.sync.RexProSyncConnectionPool'),
    'eventlet': ('rexpro.connectors.reventlet.RexProEventletSocket',
                 'rexpro.connectors.reventlet.RexProEventletConnection',
                 'rexpro.connectors.reventlet.RexProEventletConnectionPool'),
    'gevent': ('rexpro.connectors.rgevent.RexProGeventSocket',
               'rexpro.connectors.rgevent.RexProGeventConnection',
               'rexpro.connectors.rgevent.RexProGeventConnectionPool')
}
