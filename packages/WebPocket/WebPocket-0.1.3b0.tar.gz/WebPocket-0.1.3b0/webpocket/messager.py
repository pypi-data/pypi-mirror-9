# -*- coding: utf-8 -*-

from message import Message

class Messager(object):
  def __init__(self, actors):
    self._actors = actors
    self._buffer = b''

  def send_text(self, text):
    self._actors['framer'].send_text(text)

  def send_binary(self, binary):
    self._actors['framer'].send_binary(binary)

  def feed(self, frame):
    if frame.is_control():
      message_type = Message.map_type(frame.opcode)
      self._actors['pocket'].feed(Message(message_type, frame.payload))
    else:
      self._buffer += frame.payload
      if frame.fin == 0x1:
        message_type = Message.map_type(frame.opcode)
        self._actors['pocket'].feed(Message(message_type, self._buffer))
        self._buffer = b''

  def send_pong(self):
    self._actors['framer'].send_pong()

  def send_close(self, code, reason):
    self._actors['framer'].send_close(code, reason)

if __name__ == '__main__':
  class DummyPocket(object):
    def feed(self, message):
      print message.type
      print message.body

  pocket = DummyPocket()
  messager = Messager({'pocket': pocket})

  from frame import Frame
  f = Frame(payload='foobar')
  f.encode()

  messager.feed(f)
