from argparse import ArgumentParser


class Config(object):
    @staticmethod
    def unicodify(s):
        return unicode(s, 'utf8')

    @staticmethod
    def parse():
        parser = ArgumentParser()
        parser.add_argument(
            '--url', help='The WebSocket URL', default='ws://localhost:9999',
        )

        parser.add_argument(
            '--username', '-u', default='z', type=Config.unicodify,
        )
        parser.add_argument(
            '--password', default='z', type=Config.unicodify,
        )

        parser.add_argument(
            '--no-stdout', action='store_false', dest='stdout', default=True,
            help='Do not log to stdout'
        )
        parser.add_argument(
            '--debug', '-d', default=False, action='store_true',
            help='Warning: Turning on debug will display passwords.'
        )

        return parser.parse_args()
