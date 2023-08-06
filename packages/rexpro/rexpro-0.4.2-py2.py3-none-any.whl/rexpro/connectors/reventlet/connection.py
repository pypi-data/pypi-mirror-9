from eventlet.green.socket import socket as esocket
from eventlet.queue import Queue as eQueue
from eventlet.green.select import select as eselect

from rexpro.connectors.base import RexProBaseConnection, RexProBaseConnectionPool

import struct

from rexpro import exceptions
from rexpro import messages


class RexProEventletSocket(esocket):
    """ Subclass of eventlet's socket that sends and received rexpro messages

    inherits from eventlet.green.socket.socket
    """

    def send_message(self, msg):
        """
        Serializes the given message and sends it to rexster

        :param msg: the message instance to send to rexster
        :type msg: RexProMessage
        """
        self.send(msg.serialize())

    def get_response(self):
        """
        gets the message type and message from rexster


        Basic Message Structure:  reference: https://github.com/tinkerpop/rexster/wiki/RexPro-Messages

        +---------------------+--------------+---------------------------------------------------------+
        | segment             | type (bytes) | description                                             |
        +=====================+==============+=========================================================+
        | protocol version    | byte (1)     | Version of RexPro, should be 1                          |
        +---------------------+--------------+---------------------------------------------------------+
        | serializer type     | byte (1)     | Type of Serializer: msgpack==0, json==1                 |
        +---------------------+--------------+---------------------------------------------------------+
        | reserved for future | byte (4)     | Reserved for future use.                                |
        +---------------------+--------------+---------------------------------------------------------+
        | message type        | byte (1)     | Tye type of message as described in the value columns.  |
        +---------------------+--------------+---------------------------------------------------------+
        | message size        | int (4)      | The length of the message body                          |
        +---------------------+--------------+---------------------------------------------------------+
        | message body        | byte (n)     | The body of the message itself. The Good, Bad and Ugly. |
        +---------------------+--------------+---------------------------------------------------------+



        Message Types:

        +--------------+----------+-------+---------------------------------------------------------------+
        | message type | type     | value | description                                                   |
        +==============+==========+=======+===============================================================+
        | session      | request  | 1     | A request to open or close the session with the RexPro Server |
        +--------------+----------+-------+---------------------------------------------------------------+
        | session      | response | 2     | RexPro server response to session request                     |
        +--------------+----------+-------+---------------------------------------------------------------+
        | script       | request  | 3     | A request to process a gremlin script                         |
        +--------------+----------+-------+---------------------------------------------------------------+
        | script       | response | 5     | A response to a script request                                |
        +--------------+----------+-------+---------------------------------------------------------------+
        | error        | response | 0     | A RexPro server error response                                |
        +--------------+----------+-------+---------------------------------------------------------------+

        :returns: RexProMessage
        """
        msg_version = self.recv(1)
        if not msg_version:  # pragma: no cover
            # Can only be tested against a known broken version - none known yet.
            raise exceptions.RexProConnectionException('socket connection has been closed')
        if bytearray(msg_version)[0] != 1:  # pragma: no cover
            # Can only be tested against a known broken version - none known yet.
            raise exceptions.RexProConnectionException('unsupported protocol version: {}'.format(msg_version))

        serializer_type = self.recv(1)
        if bytearray(serializer_type)[0] != 0:  # pragma: no cover
            # Can only be tested against a known broken version - none known yet.
            raise exceptions.RexProConnectionException('unsupported serializer version: {}'.format(serializer_type))

        # get padding
        self.recv(4)

        msg_type = self.recv(1)
        msg_type = bytearray(msg_type)[0]

        msg_len = struct.unpack('!I', self.recv(4))[0]

        if msg_len == 0:  # pragma: no cover
            # This shouldn't happen unless there is a server-side problem
            raise exceptions.RexProScriptException("Insufficient data received")

        #response = ''
        #while len(response) < msg_len:
        #    response += self.recv(msg_len)
        response = bytearray()
        while msg_len > 0:
            chunk = self.recv(msg_len)
            response.extend(chunk)
            msg_len -= len(chunk)

        MessageTypes = messages.MessageTypes

        type_map = {
            MessageTypes.ERROR: messages.ErrorResponse,
            MessageTypes.SESSION_RESPONSE: messages.SessionResponse,
            MessageTypes.SCRIPT_RESPONSE: messages.MsgPackScriptResponse
        }

        if msg_type not in type_map:  # pragma: no cover
            # this shouldn't happen unless there is an unknown rexpro version change
            raise exceptions.RexProConnectionException("can't deserialize message type {}".format(msg_type))
        return type_map[int(msg_type)].deserialize(response)


class RexProEventletConnection(RexProBaseConnection):
    """ Eventlet-based RexProConnection """

    SOCKET_CLASS = RexProEventletSocket

    def _select(self, rlist, wlist, xlist, timeout=None):
        return eselect(rlist, wlist, xlist, timeout=timeout)


class RexProEventletConnectionPool(RexProBaseConnectionPool):
    """ Eventlet-based RexProConnectionPool """

    QUEUE_CLASS = eQueue
    CONN_CLASS = RexProEventletConnection

