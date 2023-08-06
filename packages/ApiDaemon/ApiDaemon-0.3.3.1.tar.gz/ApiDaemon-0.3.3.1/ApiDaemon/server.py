import asyncio
import json
import yaml
import traceback


class Server:
    def __init__(self, host=None, port=None, config=None, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._plugins = dict()
        self._notificator = None

        if config is not None:
            self.config = yaml.load(open(config))
            host = self.config.get('host')
            port = self.config.get('port')
            self._plugins = self.init_addons(self.config.get('plugins', {}))
            notificator = self.config.get('notificator')
            if notificator and notificator['__enabled__']:
                self._notificator = self.init_addon_instance(notificator)

        self._server = asyncio.start_server(
            self.handle_msg, host, port, loop=self._loop)

    def get_loop(self):
        return self._loop

    def prepare_addon_params(self, params):
        result = {'loop': self._loop}
        if params.get('__use_notify__'):
            result['notify'] = self.notify

        for key, value in params.items():
            if key.startswith('__'):
                continue
            result[key] = value

        return result

    def init_addon_instance(self, params):
        if params.get('__enabled__'):
            return params.get('__class__')(**self.prepare_addon_params(params))

    def init_addons(self, settings):
        result = {}
        for addon_name, params in settings.items():
            result[addon_name] = self.init_addon_instance(params)
        return result

    @asyncio.coroutine
    def notify(self, **kwargs):
        yield from self._notificator.send(**kwargs)

    def start(self, and_loop=True):
        self._server = self._loop.run_until_complete(self._server)
        if and_loop:
            self._loop.run_forever()

    def stop(self, and_loop=True):
        self._server.close()
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

    def format_error(self, exception, trace, addr, request):
        template = '''
            Exception: {}
            Address: {}
            Request: {}

            Traceback:
            {}
        '''
        return template.format(repr(exception), addr, request, trace)

    @asyncio.coroutine
    def handle_msg(self, reader, writer):
        request = yield from reader.read(1048576)

        try:
            response = yield from self.process_msg(request)
            answer = {'error': None, 'data': response}
        except Exception as e:
            answer = {'error': repr(e), 'data': None}
            yield from self.notify(
                text=self.format_error(
                    exception=e,
                    trace=traceback.format_exc(),
                    addr=writer.get_extra_info('peername'),
                    request=request.decode()
                ),
                subject='General Exception'
            )

        writer.write(json.dumps(answer).encode())
        yield from writer.drain()
        writer.close()
