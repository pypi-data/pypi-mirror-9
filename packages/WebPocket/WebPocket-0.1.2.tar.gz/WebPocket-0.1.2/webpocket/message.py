# -*- coding: utf-8 -*-

from frame import *

class Message(object):
  def __init__(self, type_, body):
    self.type = type_
    self.body = body

  @staticmethod
  def map_type(opcode):
    opcodes2type = {
      OPCODE_TEXT: 'text',
      OPCODE_BINARY: 'binary',
      OPCODE_CLOSE: 'close',
      OPCODE_PING: 'ping',
      OPCODE_PONG: 'pong'
    }
    return opcodes2type[opcode]

if __name__ == '__main__':
  print Message.map_type(OPCODE_CLOSE)
