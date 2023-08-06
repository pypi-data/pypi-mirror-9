from ApiDaemon import ApiServer
from textwrap import dedent
import logging
import click


@click.command()
@click.option('-c', '--config', type=click.Path(exists=True), help='Path to config-file.')
@click.option('--genconfig', is_flag=True, help='Path to config-file.')
def main(config, genconfig):
    if genconfig:
        print(generate_config())
        return

    if config:
        logging.basicConfig(level=logging.INFO)
        server = ApiServer(config=config)
        try:
            server.start()
        except KeyboardInterrupt:
            pass
        finally:
            server.stop()


def generate_config():
    return dedent('''
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
    ''').strip()


if __name__ == '__main__':
    main()
