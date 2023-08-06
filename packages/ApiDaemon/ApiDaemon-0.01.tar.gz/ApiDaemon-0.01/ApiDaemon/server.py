import asyncio
import logging
import json
import yaml

class Server:
    def __init__(self, host=None, port=None, config=None, loop=None):
        logging.info('Init server')
        self._loop = loop or asyncio.get_event_loop()
        self._plugins = dict()
        if config is not None:
            config = yaml.load(open(config))
            host = config.get('host')
            port = config.get('port')
            self.init_plugins(config.get('plugins', {}))

        self._server = asyncio.start_server(
            self.handle_msg, host, port, loop=self._loop)

    def get_loop(self):
        return self._loop

    def init_plugins(self, settings):
        for plugin_name, params in settings.items():
            classname = params.get('__class__')
            if params['enabled']:
                del params['__class__']
                del params['enabled']
                self._plugins[plugin_name] = classname(
                    loop=self._loop,
                    **settings.get(plugin_name, {})
                )

    def start(self, and_loop=True):
        self._server = self._loop.run_until_complete(self._server)
        logging.info(
            'Listening on {0}'.format(self._server.sockets[0].getsockname()))
        if and_loop:
            self._loop.run_forever()

    def stop(self, and_loop=True):
        self._server.close()
        logging.info('Server closed')
        if and_loop:
            self._loop.close()

    @asyncio.coroutine
    def process_msg(self, request):
        request = json.loads(request.decode())
        api, *methods = request['method'].split('.')

        wrapper = self._plugins.get(api)
        for m in methods:
            wrapper = getattr(wrapper, m)

        return (yield from wrapper(**request['parameters']))


    @asyncio.coroutine
    def handle_msg(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info('Message from {}'.format(addr))

        request = yield from reader.read(1048576)
        message = request.decode()
        logging.info('    {}'.format(message))

        try:
            response = yield from self.process_msg(request)
            answer = {'error': None, 'data': response}
        except Exception as e:
            answer = {'error': repr(e), 'data': None}

        logging.info('Prepare reply to {}'.format(addr))
        writer.write(json.dumps(answer).encode())
        yield from writer.drain()
        logging.info('Reply send')
        writer.close()
        logging.info('Close the client socket')
