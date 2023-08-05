# -*- coding: utf-8 -*-

from base64 import b64encode
import os
from hashlib import sha1
from exc import *

class Handshaker(object):
  def __init__(self, actors, host, port=80, path='/'):
    self._actors = actors
    self.host = host
    self.port = port
    self.path = path
    self.key = None
    self._buffer = ''

  def feed(self, data):
    self._buffer += data
    if '\r\n\r\n' in self._buffer:
      return self.handle_handshake()
    else:
      return False

  def handle_handshake(self):
    header_part, _, body = self._buffer.partition('\r\n\r\n')
    response, _, headers = header_part.lower().partition('\r\n')

    # `HTTP/1.1 101 Switching Protocols`
    protocol, code, status = response.split(' ', 2)
    if code != '101':
      raise WebSocketProtocolError('Invalid handshake response: %s %s' % (code, status))

    header_dict = {}
    for line in headers.split('\r\n'):
      # for the `Date` sucker
      header, value = line.split(':', 1)
      header_dict[header.strip()] = value.strip()

    if header_dict.get('upgrade') != 'websocket':
      raise WebSocketProtocolError('Invalid upgrade header: %s' % header_dict.get('upgrade'))
    if header_dict.get('connection') != 'upgrade':
      raise WebSocketProtocolError('Invalid connection header: %s' % header_dict.get('connection'))

    challenge = b64encode(sha1(self.key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
    if header_dict.get('sec-websocket-accept') != challenge.lower():
      raise WebSocketProtocolError('Invalid challenge value: %s' % header_dict.get('sec-websocket-accept'))

    self._buffer = ''
    self._actors['pocket'].on_open()
    return True

  @property
  def handshake_request(self):
    r = []
    r.append('GET %s HTTP/1.1' % self.path)
    r.append('Host: %s:%d' % (self.host, self.port))
    r.append('Upgrade: websocket')
    r.append('Connection: Upgrade')
    self.key = b64encode(os.urandom(16))
    r.append('Sec-WebSocket-Key: %s' % self.key)
    r.append('Sec-WebSocket-Version: 13')
    r.append('\r\n')
    return '\r\n'.join(r)

if __name__ == '__main__':
  shaker = Handshaker({}, 'localhost')
  print shaker.handshake_request

  r = []
  r.append('HTTP/1.1 101 Switching Protocols')
  r.append('Upgrade: websocket')
  r.append('Connection: Upgrade')
  r.append('Sec-WebSocket-Accept: InvalidChallenge')
  r.append('\r\nDummyBody')
  data = '\r\n'.join(r)

  print shaker.feed(data[:15])
  print shaker.feed(data[15:])
