import json
from tornado import gen, httpclient as hc

from . import AbstractHandler, LOGGER


class HipChatHandler(AbstractHandler):

    name = 'hipchat'

    # Default options
    defaults = {
        'room': None,
        'key': None,
    }

    colors = {
        'critical': 'red',
        'warning': 'magenta',
        'normal': 'green',
    }

    def init_handler(self):
        self.room = self.options.get('room')
        self.key = self.options.get('key')
        assert self.room, 'Hipchat room is not defined.'
        assert self.key, 'Hipchat key is not defined.'
        self.client = hc.AsyncHTTPClient()

    @gen.coroutine
    def notify(self, level, *args, **kwargs):
        LOGGER.debug("Handler (%s) %s", self.name, level)

        data = {
            'message': self.get_short(level, *args, **kwargs).decode('UTF-8'),
            'notify': True,
            'color': self.colors.get(level, 'gray'),
            'message_format': 'text',
        }

        yield self.client.fetch('https://api.hipchat.com/v2/room/{room}/notification?auth_token={token}'.format(room=self.room, token=self.key),
            headers={'Content-Type': 'application/json'}, method='POST', body=json.dumps(data))
