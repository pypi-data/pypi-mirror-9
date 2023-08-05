#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from multiprocessing import Process, Queue

from pyradio.log import Log
from pyradio.player import MpPlayer

from . import PY3
input = input if PY3 else raw_input


class CustomMpPlayer(MpPlayer):
    def __init__(self, *args, **kwargs):
        super(CustomMpPlayer, self).__init__(*args, **kwargs)

    def _buildStartOpts(self, *args, **kwargs):
        # opts is like [PLAYER_CMD, "arg1", "arg2", ..., "argN", streamUrl]
        opts = super(CustomMpPlayer, self)._buildStartOpts(*args, **kwargs)
        opts.insert(1, '-loop')
        opts.insert(2, '0')
        return opts


class RadioWrapped(object):

    def __init__(self, url=None):
        self.url = url
        self._log = Log()
        self._player = CustomMpPlayer(self._log)

    def play(self, url=None):
        self.url = url or self.url
        if self.url is not None:
            self._player.play(self.url)

    def stop(self):
        if self.is_playing():
            self._player.close()

    def pause(self):
        if self.is_playing():
            self._player.pause()

    def unpause(self):
        if not self.is_playing():
            self._player.pause()

    def toggle_pause(self):
        self._player.pause()

    def is_playing(self):
        return self._player.isPlaying()

    def get_url(self):
        return self.url


class Radio(object):

    @staticmethod
    def radio_process():
        def _radio_process(cmd_queue, answer_queue):
            radio = RadioWrapped()
            while True:
                try:
                    msg = cmd_queue.get()
                except KeyboardInterrupt:
                    return
                if msg['type'] == 'play':
                    url = msg.get('url')
                    radio.play(url)
                elif msg['type'] == 'stop':
                    radio.stop()
                elif msg['type'] == 'pause':
                    radio.pause()
                elif msg['type'] == 'unpause':
                    radio.unpause()
                elif msg['type'] == 'toggle_pause':
                    radio.toggle_pause()
                elif msg['type'] == 'is_playing':
                    answer_queue.put(radio.is_playing())
                elif msg['type'] == 'get_url':
                    answer_queue.put(radio.get_url())
                elif msg['type'] == 'EXIT':
                    return
        cmd_queue, answer_queue = Queue(), Queue()
        process = Process(target=_radio_process, args=[cmd_queue, answer_queue])
        process.daemon = True
        process.start()
        return process, cmd_queue, answer_queue

    def __init__(self):
        self.process, self.cmd_queue, self.answer_queue = Radio.radio_process()

    def play(self, url=None):
        self.cmd_queue.put({
            'type': 'play',
            'url': url,
        })

    def stop(self):
        self.cmd_queue.put({'type': 'stop'})

    def pause(self):
        self.cmd_queue.put({'type': 'pause'})

    def unpause(self):
        self.cmd_queue.put({'type': 'unpause'})

    def toggle_pause(self):
        self.cmd_queue.put({'type': 'toggle_pause'})

    def get_is_playing(self):
        self.cmd_queue.put({'type': 'is_playing'})
        return self.answer_queue.get()

    @property
    def is_playing(self): return self.get_is_playing()

    def get_url(self):
        self.cmd_queue.put({'type': 'get_url'})
        return self.answer_queue.get()

    @property
    def url(self): return self.get_url()

    def kill(self):
        self.cmd_queue.put({'type': 'EXIT'})
        self.process.join()
