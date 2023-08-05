from autobahn.twisted.wamp import ApplicationSession
import time

from twisted.internet.defer import inlineCallbacks

from twisted.internet import reactor


class Client(ApplicationSession, object):
    def onConnect(self):
        print('Connected!')
        print('Sending username: "{}"'.format(
            self.config.extra.username,
        ))
        self.join(u'paygroove', [u'ticket'], self.config.extra.username)

    def onChallenge(self, challenge):
        if challenge.method != u'ticket':
            raise Exception('Unknown challenge method')

        print('Sending password...')
        return self.config.extra.password

    def onJoin(self, details):
        return self.main(details)

    def main(self, details):
        raise NotImplementedError()

    def onDisconnect(self):
        print('Disconnected...')
        reactor.stop()


class BackgroundClient(Client):
    @inlineCallbacks
    def main(self, details):
        print('Threaded starting...')
        out_queue = self.config.extra.out_queue
        in_queue = self.config.extra.in_queue
        while True:
            action, method, args, kwargs = out_queue.get()

            if action == 'call':
                print('Calling', method)
                try:
                    response = yield self.call(method, *args, **kwargs)
                    in_queue.put((True, response))
                except Exception, e:
                    in_queue.put((False, e))

            elif action == 'close':
                print('Closing')
                self.leave()
                return

            else:
                print('Unknown action: {}'.format(call))
