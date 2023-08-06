class AIQPYException(Exception):
    pass


class ConnectionError(AIQPYException):
    pass


class LoginError(AIQPYException):
    pass


class MalformedURLException(AIQPYException):
    pass


class MissingEndpointException(AIQPYException):
    pass


class OrganizationNotFoundException(AIQPYException):
    pass


class PlatformResponseException(AIQPYException):
    pass


class PlatformException(AIQPYException):
    def __init__(self, http_status, message):
        self.http_status = http_status
        self.message = message

    def __str__(self):
        return 'HTTP %d received on request. Message from platform: %s' % \
            (self.http_status, self.message)
