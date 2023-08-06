import logging
import os

from aj.api import *

from terminal import *


@service
class TerminalManager(object):
    def __init__(self, context):
        self.context = context
        self.terminals = {}

    def __getitem__(self, _id):
        return self.terminals[_id]

    def __contains__(self, _id):
        return _id in self.terminals

    def list(self):
        return [{
            'id': _id,
            'command': self[_id].command,
        } for _id in self.terminals.keys()]

    def create(self, **kwargs):
        _id = os.urandom(32).encode('hex')
        t = Terminal(self, _id, **kwargs)
        logging.info('Created terminal %s', _id)
        self.terminals[_id] = t
        return _id

    def kill(self, _id):
        self.terminals[_id].kill()
        self.remove(_id)

    def remove(self, _id):
        self.terminals.pop(_id)
