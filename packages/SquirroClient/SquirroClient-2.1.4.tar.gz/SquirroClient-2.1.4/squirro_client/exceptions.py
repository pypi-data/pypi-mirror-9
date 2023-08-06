class SquirroError(Exception):
    """Generic Squirro exception class. All errors should be instantiated by
    providing the HTTP status code from Squirro API and if present the
    corresponding error message.
    """

    @property
    def status_code(self):
        """Returns the HTTP status code that was returned by the Squirro API
        service or `None` if no status code is present.
        """
        ret = None
        if len(self.args) > 0:
            ret = self.args[0]
        return ret

    @property
    def error(self):
        """Returns the error message that was returned by the Squirro API
        service or `None` if no message is present.
        """
        ret = None
        if len(self.args) > 1:
            ret = self.args[1]
        if not isinstance(ret, basestring):
            ret = unicode(ret)
        return ret


class ClientError(SquirroError):
    """Error raised due to invalid input from the client."""

    @property
    def data(self):
        """Returns the data returned by the Squirro API service or `None` if
        no data is present.
        """
        ret = None
        if len(self.args) > 2:
            ret = self.args[2]
        return ret


class InputDataError(ClientError):
    """Error raised due to invalid data."""
    pass


class AuthenticationError(ClientError):
    """Error raised due to invalid authentication credentials."""
    pass


class AuthorizationError(ClientError):
    """Error raised due to insufficient permissions."""
    pass


class NotFoundError(ClientError):
    """Error raised due to the requested resource not being found."""
    pass


class ConflictError(ClientError):
    """Error raised if there is a conflict in the request."""
    pass


class TransportError(SquirroError):
    """Error raised due to failed data transport."""
    pass


class RetryError(SquirroError):
    """Error raised due to failed retries"""
    pass


class ConnectionError(SquirroError):
    """Error raised due to connectivity problems."""
    pass


class UnknownError(SquirroError):
    """Class for any unknown error."""
    pass
