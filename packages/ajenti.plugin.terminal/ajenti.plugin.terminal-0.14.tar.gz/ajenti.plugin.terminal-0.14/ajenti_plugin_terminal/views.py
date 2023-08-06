from PIL import Image, ImageDraw

import json
import StringIO

from aj.api import *
from aj.api.http import url, HttpPlugin, SocketEndpoint
from aj.plugins.core.api.endpoint import endpoint

from .manager import TerminalManager


@component(HttpPlugin)
class Handler(HttpPlugin):
    def __init__(self, context):
        self.context = context
        self.mgr = TerminalManager.get(self.context)

    @url('/api/terminal/list')
    @endpoint(api=True)
    def handle_list(self, http_context):
        return self.mgr.list()

    @url('/api/terminal/create')
    @endpoint(api=True)
    def handle_create(self, http_context):
        options = json.loads(http_context.body)
        return self.mgr.create(**options)

    @url(r'/api/terminal/kill/(?P<terminal_id>.+)')
    @endpoint(api=True)
    def handle_kill(self, http_context, terminal_id=None):
        return self.mgr.kill(terminal_id)

    @url(r'/api/terminal/full/(?P<terminal_id>.+)')
    @endpoint(api=True)
    def handle_full(self, http_context, terminal_id=None):
        if terminal_id in self.mgr:
            return self.mgr[terminal_id].format(full=True)
        else:
            return None

    colors = {
        'black': '#073642',
        'white': '#eee8d5',
        'green': '#859900',
        'yellow': '#b58900',
        'red': '#dc322f',
        'magenta': '#d33682',
        'violet': '#6c71c4',
        'blue': '#268bd2',
        'cyan': '#2aa198',
    }

    @url(r'/api/terminal/preview/(?P<terminal_id>.+)')
    @endpoint(page=True)
    def handle_preview(self, http_context, terminal_id):
        terminal = self.mgr[terminal_id]

        img = Image.new('RGB', (terminal.width, terminal.height * 2))
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [0, 0, terminal.width, terminal.height],
            fill=ImageDraw.ImageColor.getcolor(self.colors['black'], 'RGB')
        )

        for y in range(0, terminal.height):
            for x in range(0, terminal.width):
                fc = terminal.screen.buffer[y][x][1]
                if fc == 'default':
                    fc = 'lightgray'
                if fc in self.colors:
                    fc = self.colors[fc]
                fc = ImageDraw.ImageColor.getcolor(fc, 'RGB')
                bc = terminal.screen.buffer[y][x][2]
                if bc == 'default':
                    bc = 'black'
                if bc in self.colors:
                    bc = self.colors[bc]
                bc = ImageDraw.ImageColor.getcolor(bc, 'RGB')
                ch = terminal.screen.buffer[y][x][0]
                draw.point((x, y * 2 + 1), fill=(fc if ord(ch) > 32 else bc))
                draw.point((x, y * 2), fill=bc)

        sio = StringIO.StringIO()
        img.save(sio, 'PNG')

        http_context.add_header('Content-Type', 'image/png')
        http_context.respond_ok()
        return sio.getvalue()


@component(SocketEndpoint)
class Socket(SocketEndpoint):
    plugin = 'terminal'

    def __init__(self, context):
        SocketEndpoint.__init__(self, context)
        self.mgr = TerminalManager.get(self.context)
        self.readers = {}

    def on_message(self, message, *args):
        terminal_id = message['id']
        if terminal_id not in self.mgr:
            self.send({
                'id': terminal_id,
                'type': 'closed',
            })
            return
        if message['action'] == 'subscribe':
            if terminal_id in self.readers:
                self.readers[terminal_id].kill(block=False)
            self.readers[terminal_id] = self.spawn(self.reader, terminal_id)
        if message['action'] == 'input':
            terminal = self.mgr[terminal_id]
            terminal.feed(message['data'])
        if message['action'] == 'resize':
            terminal = self.mgr[terminal_id]
            terminal.resize(message['width'], message['height'])

    def reader(self, terminal_id):
        terminal = self.mgr[terminal_id]
        q = terminal.output.register()
        while True:
            self.send({
                'type': 'data',
                'id': terminal_id,
                'data': q.get(),
            })
