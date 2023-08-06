import socket
import json
from ApiDaemon.clients.response import Response

class SyncClient():
    def __init__(self, host, port, size=1048576):
        self.host = host
        self.port = port
        self.size = size

    def send(self, method, **kwargs):
        request = {
            'method': method,
            'parameters': kwargs
        }
        message = json.dumps(request)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(message.encode())
        data = s.recv(self.size)
        s.close()
        return data

    def __getattr__(self, item):
        return Request(self, [item])


class Request:
    def __init__(self, sender, chain):
        self._sender = sender
        self.chain = chain

    def __getattr__(self, item):
        return Request(self._sender, self.chain+[item])

    def __call__(self, *args, **kwargs):
        method = '.'.join(self.chain)
        result = json.loads(self._sender.send(method, **kwargs).decode())

        return Response(method=method, kwargs=kwargs, **result)
