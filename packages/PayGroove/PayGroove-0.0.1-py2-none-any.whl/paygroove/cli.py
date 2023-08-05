from .client import Client
from .config import Config
from .connection import Connection


class CommandLineClient(Client):
    def main(self, details):
        yield self.call('com.paygroove.rpc.players.list')


def main():
    config = Config.parse()

    connection = Connection(config)
    # pg.run_background()

if __name__ == '__main__':
    main()
