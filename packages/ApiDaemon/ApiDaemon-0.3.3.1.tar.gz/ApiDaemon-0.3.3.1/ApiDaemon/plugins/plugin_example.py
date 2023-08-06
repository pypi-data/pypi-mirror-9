import asyncio
import ApiDaemon


class MyBar:
    def __init__(self, bar_name, notify=None, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self.bar_name = bar_name
        self.notify = notify
        self._menu = [
            'Beer',
            'Chips',
            'Steak'
        ]

    @asyncio.coroutine
    def is_open(self):
        return 'yes'

    @asyncio.coroutine
    def greeting(self, name):
        return 'Hello, {}. Welcome to {}'.format(name, self.bar_name)

    @asyncio.coroutine
    def menu(self):
        return self._menu


    @asyncio.coroutine
    @ApiDaemon.RateLimited(1)
    def long_request(self, sleep_time):
        print('asyncio.sleep(int({}))'.format(sleep_time))
        yield from asyncio.sleep(int(sleep_time))
        return 'Sleep {} seconds'.format(str(sleep_time))


    @asyncio.coroutine
    def order(self, item):
        if item in self._menu:
            return {'Order': item, 'Price': '5$'}
        else:
            raise ApiDaemon.ApiException('No item in menu')

    @asyncio.coroutine
    def try_robbery(self):
        yield from self.notify(text='Administrator, call police! we were robbed!')
