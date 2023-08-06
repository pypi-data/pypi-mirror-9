import asyncio
import json
from ApiDaemon.clients.response import Response

class Client:
    def __init__(self, host, port, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.host = host
        self.port = port

    @asyncio.coroutine
    def send(self, method, **kwargs):
        request = {
            'method': method,
            'parameters': kwargs
        }
        message = json.dumps(request)
        reader, writer = yield from asyncio.open_connection(
            self.host, self.port, loop=self.loop)
        writer.write(message.encode())
        yield from writer.drain()
        data = yield from reader.read(1048576)
        writer.close()
        return data

    def __getattr__(self, item):
        return AsyncRequest(self, [item])


class AsyncRequest:
    def __init__(self, sender, chain):
        self._sender = sender
        self.chain = chain

    def __getattr__(self, item):
        return AsyncRequest(self._sender, self.chain+[item])

    @asyncio.coroutine
    def __call__(self, *args, **kwargs):
        method = '.'.join(self.chain)
        response = yield from self._sender.send(method, **kwargs)
        result = json.loads(response.decode())
        return Response(method=method, kwargs=kwargs, **result)
