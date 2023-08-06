from ApiDaemon.exceptions import ApiException

class Response:
    def __init__(self, method, args, error, data):
        self.method = method
        self.error = error
        self.args = args
        self.data = data

    def __repr__(self):
        if self.error:
            raise ApiException('Error: {}'.format(self.error))
        else:
            return repr(self.data)
