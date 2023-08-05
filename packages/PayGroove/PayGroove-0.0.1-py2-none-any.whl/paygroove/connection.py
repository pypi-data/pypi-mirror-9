import atexit
import sys
from multiprocessing import Process, Queue

from autobahn.twisted.wamp import ApplicationRunner
from autobahn.twisted.websocket import WebSocketClientFactory
from twisted.internet import ssl
from twisted.python import log

from paygroove.client import BackgroundClient
from paygroove.exception import PayGrooveException
from paygroove.models import Player, BitcoinAddress, Transaction


class Connection(object):
    def __init__(self, config):
        self.config = config

    def create_factory(self, client_class):
        factory = WebSocketClientFactory(self.config.url, debug=True)
        factory.protocol = client_class

        if factory.isSecure:
            context_factory = ssl.ClientContextFactory()
        else:
            context_factory = None

        return factory, context_factory

    def run(self, client_class):
        if self.config.stdout:
            log.startLogging(sys.stdout)

        runner = ApplicationRunner(
            self.config.url,
            u'paygroove',
            extra=self.config,
            debug=self.config.debug,
            debug_wamp=self.config.debug,
            debug_app=self.config.debug,
        )
        runner.run(client_class)


class BackgroundConnection(Connection):
    def __init__(self, config):
        Connection.__init__(self, config)
        self.out_queue = Queue()
        self.in_queue = Queue()
        self.process = None

    def run(self, client=None):
        if not client:
            client = BackgroundClient

        self.config.out_queue = self.out_queue
        self.config.in_queue = self.in_queue
        self.process = Process(
            target=Connection.run,
            args=(self, client)
        )
        self.process.start()

        # Automatically exit the process when the parent process quits
        atexit.register(self.close)

    def call(self, method, *args, **kwargs):
        if not self.process:
            raise RuntimeError('Process not running. Try calling run() first.')

        self.out_queue.put(('call', method, args, kwargs))
        ok, response = self.in_queue.get()
        if ok:
            return response
        else:
            raise PayGrooveException(response)

    def close(self):
        self.out_queue.put(('close', None, None, None))
        self.process.join()


class PayGrooveConnection(BackgroundConnection):
    def __init__(self, config):
        BackgroundConnection.__init__(self, config)
        self.player = PayGrooveConnection.RPCPlayer(self)
        self.wallet = PayGrooveConnection.RPCWallet(self)

    def rpc(self, method, *args, **kwargs):
        prefix = 'com.paygroove.rpc.'
        return self.call('{}{}'.format(prefix, method), *args, **kwargs)

    class RPCPlayer(object):
        def __init__(self, parent):
            self.parent = parent
            self.address = PayGrooveConnection.RPCAddress(self.parent)

        def find(self, player=None):
            players = self.parent.rpc('player.find', player=player)['results']
            for player in players:
                yield Player.from_dict(player)

        def create(self, player):
            return Player.from_dict(
                self.parent.rpc('player.create', player=player)
            )

    class RPCAddress(object):
        def __init__(self, parent):
            self.parent = parent

        def generate(self, player):
            data = self.parent.rpc('player.address.generate', player=player)
            return BitcoinAddress.from_dict(data)

    class RPCWallet(object):
        def __init__(self, parent):
            self.parent = parent

        def transactions(self, player=None):
            data = self.parent.rpc('wallet.transactions', player=player)
            for transaction in data:
                yield Transaction.from_dict(transaction)

        def balance(self, player=None):
            return self.parent.rpc('wallet.balance', player=player)

