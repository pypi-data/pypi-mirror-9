ApiDaemon
-----
Service for merging any external API. Now project in very-very unstable state.
Project contain three part: server (AsyncIO), asynchronous-client and synchronous-client. I think later it's must be three different projects, because async-client cannot work with python 2 and package cannot install by requirements (asyncio)

Some documentation: http://apidaemon.readthedocs.org/

Bash-usage
-----

.. code:: bash
    
    pip install ApiDaemon
    apidaemon --genconfig > config.yml
    
Than edit config.yml as you want:

.. code:: yaml

    host: 127.0.0.1
    port: 2007
    plugins:
        vk:
            __class__: !!python/name:ApiDaemon.VkPlugin
            enabled: !!bool true
            app_id: null
            user_login: null
            user_password: null
            access_token: null
        lastfm:
            __class__: !!python/name:ApiDaemon.LastfmPlugin
            enabled: !!bool true
            key: null

And just run

.. code:: bash

    apidaemon -c config.yml

Python-usage
-----

.. code:: python

    from ApiDaemon import ApiServer

    config_path = './config.yml'

    if __name__ == '__main__':
        server = ApiServer(config=config_path)

        try:
            server.start()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()




Client-side
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

    from ApiDaemon import ApiSyncClient

    sync_api = ApiSyncClient(host='127.0.0.1', port=2007)
    
    response = sync_api.lastfm.artist.getinfo(artist='Metallica')
    print(response)
    
    response = sync_api.vk.audio.get(count=2)
    print(response)
