class RexProException(Exception):
    """ Base RexProException """
    pass


class RexProInvalidConnectorTypeException(RexProException):
    """ Raised when the specified connector type isn't supported """
    pass


class RexProConnectionException(RexProException):
    """ Raised when there are problems with the rexster connection """
    pass


class RexProResponseException(RexProException):
    """ Generic Exception Message Response """
    pass


class RexProScriptException(RexProResponseException):
    """
    Raised when there's an error with a script request
    """
    pass


class RexProInvalidSessionException(RexProResponseException):
    """ An invalid or expired sessions was provided """
    pass


class RexProAuthenticationFailure(RexProResponseException):
    """ Invalid authentication credentials provided """
    pass


class RexProSerializationException(RexProResponseException):
    """ Serialization error, check your Titan Version compatibility """
    pass


class RexProGraphConfigException(RexProResponseException):
    """ Graph Configuration error

    This is a serious problem.
    """
    pass


class RexProChannelConfigException(RexProResponseException):
    """ Channel Configuration error

    This is a serious problem.
    """
    pass


class RexProInvalidMessageException(RexProResponseException):
    """ Invalid message was provided, This may be an incompatible msgpack problem """
    pass
