class RestError(Exception):
    '''
    Base rest error exception class. All other rest exception are derived from
    RestError
    '''
    def __init__(self, message, code=None):
        '''
        :param message: string -- exception message
        :param code: int -- code of the error, optional. used to be returned
        alongside meesage
        '''
        super(RestError, self).__init__(message)
        self.code = code


class BadRequestError(RestError):
    '''
    HTTP 400. Bad request
    '''
    http_code = 400


class ForbiddenError(RestError):
    '''
    HTTP 403. Forbidden
    '''
    http_code = 403


class NotFoundError(RestError):
    '''
    HTTP 404. Not found error
    '''
    http_code = 404


class MethodNotAllowedError(RestError):
    '''
    HTTP 405. HTTP method is not allowed
    '''
    http_code = 405


class ConflictError(RestError):
    '''
    HTTP 409. Conflict
    '''
    http_code = 409


class ServerError(RestError):
    '''
    HTTP 503. Internal service error
    '''
    http_code = 503
