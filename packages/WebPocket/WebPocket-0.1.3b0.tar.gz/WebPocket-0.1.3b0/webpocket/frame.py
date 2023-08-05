# -*- coding: utf-8 -*-

import os
import struct
from struct import pack, unpack
from copy import copy
from binascii import hexlify

from exc import *

OPCODE_CONTINUE = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xa

class Frame(object):
  def __init__(self, fin=0x1, opcode=OPCODE_TEXT, mask=0x1, payload=''):
    self.fin = fin
    self.opcode = opcode
    self.mask = mask
    self.payload = bytearray(payload)
    self.payload_length = len(payload)
    self.masking_key = None
    self.masked_payload = None

  def inspect(self):
    print 'FIN bit        :', self.fin
    print 'opcode         :', hex(self.opcode)
    print 'MASK bit       :', self.mask
    if self.mask == 0x1:
      print 'masking key    :', hexlify(self.masking_key)
      print 'masked payload :', hexlify(self.masked_payload)
    print 'payload length :', self.payload_length
    print 'payload        :', self.payload
    print ''

  def is_control(self):
    return self.opcode in [OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG]

  def encode(self):
    buf = pack('!B', self.fin << 7 | self.opcode)
    length = self.payload_length
    if length <= 125:
      buf += pack('!B', self.mask << 7 | length)
    elif length < (1 << 16):
      buf += pack('!B', self.mask << 7 | 126) + pack('!H', length)
    else:
      buf += pack('!B', self.mask << 7 | 127) + pack('!Q', length)

    if self.mask == 0x1:
      masking_key = os.urandom(4)
      buf += masking_key
      self.masking_key = masking_key
      masking_key = map(ord, masking_key)

      masked_payload = copy(self.payload)
      for i in range(length):
        masked_payload[i] ^= masking_key[i % 4]
      self.masked_payload = masked_payload
      buf += masked_payload
    else:
      buf += self.payload

    return str(buf)

  def decode(self, raw_data):
    try:
      first_word = unpack('!2B', raw_data[:2])
      left_data = raw_data[2:]

      if first_word[0] & 0x70 != 0:
        raise WebSocketProtocolError('Invalid RSV bits')
      self.fin = (first_word[0] & 0x80) >> 7
      self.opcode = first_word[0] & 0x0f
      if not self.opcode in [OPCODE_CONTINUE, OPCODE_TEXT, OPCODE_BINARY, OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG]:
        raise WebSocketProtocolError('Invalid opcode: ' + hex(self.opcode))
      if self.fin == 0x0 and self.opcode in [OPCODE_CLOSE, OPCODE_PING, OPCODE_PONG]:
        raise WebSocketProtocolError('Invalid FIN bit: ' + hex(self.fin))
      self.mask = (first_word[1] & 0x80) >> 7
      
      length = first_word[1] & 0x7f
      if length == 126:
        length = unpack('!H', left_data[:2])[0]
        left_data = left_data[2:]
      elif length == 127:
        length = unpack('!Q', left_data[:8])[0]
        if length >> 63 != 0:
          raise WebSocketProtocolError('Invalid payload length: ' + length)
        left_data = left_data[8:]
      self.payload_length = length

      if self.mask == 0x1:
        masking_key = {}
        self.masking_key = left_data[:4]
        for i in range(4):
          masking_key[i] = self.masking_key[i]
        self.masked_payload = left_data[4:4 + length]

        self.payload = bytearray(copy(self.masked_payload))
        for i in range(length):
          self.payload[i] ^= masking_key[i % 4]

        self.payload = str(self.payload)
        left_data = left_data[4 + length:]
      else:
        self.payload = left_data[:length]
        left_data = left_data[length:]

      if len(self.payload) != length:
        raise InsufficientBytesException()

      if self.opcode == OPCODE_CLOSE and length >= 2:
        self.payload = unpack('!H', self.payload[:2])[0]

      return self, left_data

    except (IndexError, struct.error):
      raise InsufficientBytesException()

if __name__ == '__main__':
  a = Frame(payload='foobar')
  data = a.encode()
  a.inspect()

  b, left_data = Frame().decode(data)
  b.inspect()

  payload = pack('!H', 1000) + 'Normal Closure'
  c = Frame(opcode=OPCODE_CLOSE, payload=payload)
  print hexlify(c.encode())
  c.inspect()
