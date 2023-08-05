
class AsanaError(Exception):
    def __init__(self, message=None, status=None, response=None):
        try:
            messages = [error['message'] for error in response.json()['errors']]
            message = message + ': ' + '; '.join(messages)
        except Exception:
            pass

        super(AsanaError, self).__init__(message)

        self.status = status
        self.response = response

class InvalidRequestError(AsanaError):
    def __init__(self, response=None):
        super(InvalidRequestError, self).__init__(
            message='Invalid Request',
            status=400,
            response=response
        )

class NoAuthorizationError(AsanaError):
    def __init__(self, response=None):
        super(NoAuthorizationError, self).__init__(
            message='No Authorization',
            status=401,
            response=response
        )

class ForbiddenError(AsanaError):
    def __init__(self, response=None):
        super(ForbiddenError, self).__init__(
            message='Forbidden',
            status=403,
            response=response
        )

class NotFoundError(AsanaError):
    def __init__(self, response=None):
        super(NotFoundError, self).__init__(
            message='Not Found',
            status=404,
            response=response
        )

class InvalidTokenError(AsanaError):
    def __init__(self, response=None):
        super(InvalidTokenError, self).__init__(
            message='Sync token invalid or too old',
            status=412,
            response=response
        )
        self.sync = response != None and response.json()['sync']

class RetryableAsanaError(AsanaError):
    def __init__(self, message=None, status=None, response=None):
        super(RetryableAsanaError, self).__init__(message=message, status=status, response=response)

class RateLimitEnforcedError(RetryableAsanaError):
    def __init__(self, response=None):
        super(RateLimitEnforcedError, self).__init__(
            message='Rate Limit Enforced',
            status=429,
            response=response
        )
        self.retry_after = response != None and float(response.headers['Retry-After'])

class ServerError(RetryableAsanaError):
    def __init__(self, response=None):
        super(ServerError, self).__init__(
            message='Server Error',
            status=500,
            response=response
        )
