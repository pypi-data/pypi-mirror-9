import asyncio
import requests
import json
from functools import partial

class LastfmPlugin:
    def __init__(self, key, timeout=10, response_format='json', loop=None, notify=None):
        self._loop = loop or asyncio.get_event_loop()
        self.key = key
        self.url = r'http://ws.audioscrobbler.com/2.0/'
        self.format = response_format
        self.default_timeout = timeout
        self.session = requests.Session()
        self.session.headers['Accept'] = 'application/json'

    def __getattr__(self, item):
        return AsyncRequest(self, [item])

    @asyncio.coroutine
    def send(self, method, **kwargs):
        params = {
            'method': method,
            'api_key': self.key,
            'format': self.format
        }
        params.update(kwargs)
        response = yield from self._loop.run_in_executor(
            None,
            partial(self.session.post, timeout=self.default_timeout),
            self.url,
            params
        )
        return json.loads(response.text)


class AsyncRequest:
    def __init__(self, sender, chain):
        self._sender = sender
        self.chain = chain

    def __getattr__(self, item):
        return AsyncRequest(self._sender, self.chain+[item])

    @asyncio.coroutine
    def __call__(self, *args, **kwargs):
        return (yield from self._sender.send('.'.join(self.chain), **kwargs))
