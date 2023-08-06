ApiDaemon is a service for merging any external API. Now project in very-very unstable state.

Project contain three part: server (AsyncIO), asynchronous-client and synchronous-client. I think later it's must be three different projects, because async-client cannot work with python 2 and package cannot install by requirements (asyncio)

Server
-----

.. code:: python

    from ApiDaemon import ApiServer
    from ApiDaemon import VkPlugin
    from ApiDaemon import LastfmPlugin
    
    import logging
    
    config = {
        'lastfm': {
            '__class__': LastfmPlugin,
            'key': ''
        },
        'vk': {
            '__class__': VkPlugin,
            'app_id': '',
            'user_login': '',
            'user_password': ''
        }
    }
    
    if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO)
        server = ApiServer('127.0.0.1', 2007)
        server.init_plugins(config)
    
        try:
            server.start()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()


That's all :) Universal API-server ready for connections.


Client
-----

Async client

.. code:: python

    import asyncio
    from ApiDaemon import ApiClient
    
    @asyncio.coroutine
    def main(loop=None):
        async_api = ApiClient(host='127.0.0.1', port=2007, loop=loop)
        
        response = yield from async_api.lastfm.artist.getinfo(artist='Metallica')
        print(response)
        
        response = yield from async_api.vk.users.get(user_id=1)
        print(response)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()


Synchronous client

.. code:: python

    sync_api = ApiSyncClient(host='127.0.0.1', port=2007)
    
    response = sync_api.lastfm.artist.getinfo(artist='Metallica')
    print(response)
    
    response = sync_api.vk.audio.get(count=2)
    print(response)
