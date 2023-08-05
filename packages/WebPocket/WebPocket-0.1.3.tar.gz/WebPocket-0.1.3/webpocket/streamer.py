# -*- coding: utf-8 -*-

from twisted.internet.protocol import Protocol, ReconnectingClientFactory

class Socket(Protocol):
  def connectionMade(self):
    self.transport.write(self.factory.handshaker.handshake_request)

  def dataReceived(self, data):
    if self.factory.handshaken:
      self.factory.framer.feed(data)
    else:
      result = self.factory.handshaker.feed(data)
      self.factory.handshaken = result

  def send_message(self, data):
    self.transport.write(data)

  def close_connection(self):
    self.transport.loseConnection()

class Streamer(ReconnectingClientFactory):
  def __init__(self, actors):
    self._actors = actors
    self.handshaken = False
    self.socket = None
    self.halt = True

  @property
  def handshaker(self):
    return self._actors['handshaker']

  @property
  def framer(self):
    return self._actors['framer']

  def buildProtocol(self, address):
    socket = Socket()
    self.socket = socket
    socket.factory = self
    self.resetDelay()
    self.halt = False
    return socket

  def clientConnectionLost(self, connector, reason):
    self.handshaken = False
    if not self.halt:
      ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

  def clientConnectionFailed(self, connector, reason):
    ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

  def send(self, data):
    self.socket.send_message(data)

  def close(self):
    self.halt = True
    self.socket.close_connection()

if __name__ == '__main__':
  from handshaker import Handshaker
  shaker = Handshaker('localhost', path='/api/v1/websocket')

  from twisted.internet import reactor
  streamer = Streamer(shaker, 'dummy')
  reactor.connectTCP('localhost', 80, streamer)
  reactor.run()
