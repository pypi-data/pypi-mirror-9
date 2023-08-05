# -*- coding: utf-8 -*-

from struct import pack
from frame import *
from exc import *

class Framer(object):
  def __init__(self, actors, payload_limit=0):
    self._actors = actors
    self._buffer = b''
    self._payload_limit = payload_limit

  def send_text(self, text):
    limit = self._payload_limit
    if limit > 0 and limit < len(text):
      text = self._send_fragment(0, OPCODE_TEXT, text, limit)
      while limit < len(text):
        text = self._send_fragment(0, OPCODE_CONTINUE, text, limit)
      self._send_fragment(1, OPCODE_CONTINUE, text, limit)
    else:
      data = Frame(opcode=OPCODE_TEXT, payload=text).encode()
      self._actors['streamer'].send(data)

  def send_binary(self, binary):
    limit = self._payload_limit
    if limit > 0 and limit < len(binary):
      binary = self._send_fragment(0, OPCODE_BINARY, binary, limit)
      while limit < len(binary):
        binary = self._send_fragment(0, OPCODE_CONTINUE, binary, limit)
      self._send_fragment(1, OPCODE_CONTINUE, binary, limit)
    else:
      data = Frame(opcode=OPCODE_TEXT, payload=text).encode()
      self._actors['streamer'].send(data)

  def _send_fragment(self, fin, opcode, payload, limit):
    data = Frame(fin=fin, opcode=opcode, payload=payload[:limit]).encode()
    self._actors['streamer'].send(data)
    return payload[limit:]

  def feed(self, data):
    self._buffer += data
    while len(self._buffer) > 0:
      try:
        frame, left_data = Frame().decode(self._buffer)
        self._buffer = left_data
        self._actors['messager'].feed(frame)
      except InsufficientBytesException:
        break

  def send_pong(self):
    data = Frame(opcode=OPCODE_PONG).encode()
    self._actors['streamer'].send(data)

  def send_close(self, code, reason):
    payload = pack('!H', code) + reason
    data = Frame(opcode=OPCODE_CLOSE, payload=payload).encode()
    self._actors['streamer'].send(data)

if __name__ == '__main__':
  class DummyMessager(object):
    def feed(self, frame):
      frame.inspect()

  messager = DummyMessager()
  framer = Framer({'messager': messager})

  data = Frame(payload='foobar').encode()
  framer.feed(data[:3])
  framer.feed(data[3:])
