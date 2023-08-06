# Copyright (c) 2015 Codenomicon Ltd.
# License: MIT

class AppcheckException(Exception):
    """Coderot interface exception"""


class ConnectionFailure(AppcheckException):
    """Connection to API failed"""


class OutOfRetriesError(AppcheckException):
    """Ran out of retries with a HTTP request"""


class ResultNotFound(AppcheckException):
    """Result for requested ID or SHA1 was not found"""


class InvalidLoginError(AppcheckException):
    """Login was rejected"""