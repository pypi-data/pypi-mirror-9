from ApiDaemon import ApiServer
import logging
import click
import os


@click.command()
@click.option('-c', '--config', type=click.Path(exists=True), help='Path to config-file.')
@click.option('--genconfig', is_flag=True, help='Generate simple config into stdout.')
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
    path = os.path.dirname(os.path.realpath(__file__))
    return open('{}/config_default.yml'.format(path)).read()

if __name__ == '__main__':
    main()
