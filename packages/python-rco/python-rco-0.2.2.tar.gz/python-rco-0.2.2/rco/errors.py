# -*- coding: utf-8 -*-


class BaseError (Exception):

    def __init__ (self, message, code = 1):
        super (BaseError, self).__init__ (message, code)


class SecurityError (BaseError):
    pass


class RequestError (BaseError):

    def __init__ (self, message = None):
        super (RequestError, self).__init__ (
            message or 'Invalid request',
            - 32700
        )


class MethodError (BaseError):

    def __init__ (self, message = None):
        super (MethodError, self).__init__ (
            message or 'Method not found',
            - 32601
        )
