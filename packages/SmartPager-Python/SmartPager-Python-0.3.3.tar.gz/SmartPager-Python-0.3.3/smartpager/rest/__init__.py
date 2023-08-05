

class RestException(Exception):
    pass


class InvalidRestMethodException(RestException):
    pass


class SmartPagerRestException(RestException):
    """
    Covers all 400 and 500 level HTTP response codes
    """

    def __init__(self, status_code='', url='', message='', method=''):
        self.status_code = status_code
        self.url = url
        self.message = message
        self.method = method

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.method, self.status_code, self.message, self.url)


class RestParams(object):
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
    PUT = 'PUT'

    AllowedRESTMethods = (
        GET,
        POST,
        DELETE,
        PUT,
    )