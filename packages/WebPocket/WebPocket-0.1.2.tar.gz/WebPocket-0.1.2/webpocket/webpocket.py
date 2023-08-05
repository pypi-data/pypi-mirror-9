# -*- coding: utf-8 -*-

from threading import Thread
from twisted.internet import reactor, ssl
from streamer import Streamer
from handshaker import Handshaker
from framer import Framer
from messager import Messager
from compat import urlsplit
from exc import *

class WebPocket(object):
  def __init__(self, url, run=False, **options):
    self.scheme = None
    self.host = None
    self.port = None
    self.path = None
    self._parse_url(url)

    payload_limit = options.get('payload_limit') or 0

    actors = {}
    actors['pocket'] = self
    actors['messager'] = Messager(actors)
    actors['framer'] = Framer(actors, payload_limit=payload_limit)
    actors['handshaker'] = Handshaker(actors, self.host, self.port, self.path)
    streamer = Streamer(actors)
    actors['streamer'] = streamer
    self._actors = actors

    if self.scheme == 'ws':
      reactor.connectTCP(self.host, self.port, streamer)
    elif self.scheme == 'wss':
      reactor.connectSSL(self.host, self.port, streamer, ssl.ClientContextFactory())
    else:
      raise WebSocketProtocolError('Invalid scheme: ' + self.scheme)

    self._thread = None
    if run:
      self.run()

  def send(self, message, binary=False):
    reactor.callFromThread(self._send, message, binary)

  def _send(self, message, binary):
    if binary:
      self._actors['messager'].send_binary(message)
    else:
      self._actors['messager'].send_text(message)

  def run(self):
    self._thread = Thread(target=reactor.run, args=(False,))
    self._thread.start()

  def stop(self):
    reactor.callFromThread(self._actors['streamer'].close)
    reactor.callFromThread(reactor.stop)
    self.on_close(1001)

  def feed(self, message):
    t = message.type
    if t == 'text':
      self.on_text(str(message.body))
    elif t == 'binary':
      self.on_binary(str(message.body))
    elif t == 'close':
      self._actors['messager'].send_close(1000, 'Normal Closure')
      self._actors['streamer'].close()
      reactor.stop()
      self.on_close(message.body)
    elif t == 'ping':
      self._actors['messager'].send_pong()
    elif t == 'pong':
      pass

  def on_open(self):
    pass

  def on_text(self, text):
    pass

  def on_binary(self, binary):
    pass

  def on_close(self, code):
    pass

  def _parse_url(self, url):
    parsed_url = urlsplit(url)
    self.scheme = parsed_url.scheme

    self.host = parsed_url.hostname
    if parsed_url.hostname:
      self.host = parsed_url.hostname
    else:
      raise ValueError('Invalid url: %s' % url)
    
    if parsed_url.port:
      self.port = int(parsed_url.port)

    if self.scheme == 'ws':
      if not self.port:
        self.port = 80
    elif self.scheme == 'wss':
      if not self.port:
        self.port = 443
    else:
      raise ValueError('Invalid url: %s' % url)

    if parsed_url.path:
      self.path = parsed_url.path
    else:
      self.path = '/'

    if parsed_url.query:
      self.path += '?' + parsed_url.query

if __name__ == '__main__':
  pocket = WebPocket('ws://localhost/api/v1/websocket', run=True)

  import time
  try:
    while True:
      time.sleep(3)
      pocket.send('{"action":"ping"}')
  except KeyboardInterrupt:
    pocket.stop()
