# Copyright (c) 2014 Stefan C. Mueller

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from twisted.internet import protocol, defer
import logging
from anycall import packetprotocol

logger = logging.getLogger(__name__)




class ConnectionPool(object):
    """
    To avoid opening a new connection for each communication,
    we use this class to pool them. Each connection is opened on first
    use and automatically closed if unused for a certain time. 
    

    This class has some abstract methods:
    
    * `on_receive` invoked when we receive data from a connection.
    * `create_client_endpoint` invoked when we need to open a new
      connection. This has to return a IStreamClientEndpoint such as
      a TCP4ClientEndpoint.
      
    In addition a IStreamServerEndpoint can be passed to `__init__`.
    If so, we'll listen for incomming connections and add them to
    the pool.
    """
    
    def __init__(self, stream_server_endpoint, make_client_endpoint, ownid_factory):
        """
        :param stream_server_endpoint: `IStreamServerEndpoint` implementation. We will listen
          on this for incomming connections.
          
        :param make_client_endpoint: Invoked when we need to connect to a peer. Returns 
          `IStreamClientEndpoint` implementation that we can use to connect to that peer's
          `stream_server_endpoint`.
          
        :param ownid: Identification string (such as hostname and port) that peers can use
          to connect to us.
        """
        self.stream_server_endpoint = stream_server_endpoint
        self.ownid_factory = ownid_factory
        self.make_client_endpoint = make_client_endpoint
        
        self._listeningport = None
        
        self._connections = {}
        self._ongoing_sends = set()
        
        
        self._typenames = set()
        self._dummy_protocol = packetprotocol.PacketProtocol()
        
    def register_type(self, typename):
        """
        Registers a type name so that it may be used to send and receive packages.
        
        :param typename: Name of the packet type. A method with the same name and a
            "on_" prefix should be added to handle incomming packets.
            
        :raises ValueError: If there is a hash code collision.
        """ 
        
        # this is to check for collisions only
        self._dummy_protocol.register_type(typename)
        
        self._typenames.add(typename)
        
    def open(self, packet_received):
        """
        Opens the port.
        
        :param packet_received: Callback which is invoked when we received a packet.
          Is passed the peer, typename, and data.

        :returns: Deferred that callbacks when we are ready to receive.
        """
        def port_open(listeningport):
            self._listeningport = listeningport
            self.ownid = self.ownid_factory(listeningport)
            logger.debug("Port opened. Own-ID:%s" % self.ownid)
            return None
        
        logger.debug("Opening connection pool")
        
        self.packet_received = packet_received
        d = self.stream_server_endpoint.listen(PoolFactory(self, self._typenames))
        d.addCallback(port_open)
        return d
    
    
    def send(self, peer, typename, data):
        """
        Sends a packet to a peer.
        """

        def connect():
            logger.debug("Opening connection to %s..." % peer)
            endpoint = self.make_client_endpoint(peer)
            d = endpoint.connect(PoolFactory(self, self._typenames, peer))
            d.addCallback(lambda p:p.wait_for_handshake())
            return d
        
        def attempt_to_send(_):
            if peer not in self._connections:
                d = connect()
                d.addCallback(attempt_to_send)
                return d
            else:
                conn = self._connections[peer][0]
                conn.send_packet(typename, data)            
                return defer.succeed(None)
        
        d = attempt_to_send(None)
        
        self._ongoing_sends.add(d)
        
        def send_completed(result):
            if d in self._ongoing_sends:
                self._ongoing_sends.remove(d)
            return result
        
        d.addBoth(send_completed)
        return d
    
    def close(self):
        """
        Stop listing for new connections and close all open connections.
        
        :returns: Deferred that calls back once everything is closed.
        """
        
        def cancel_sends(_):
            logger.debug("Closed port. Cancelling all on-going send operations...")
            while self._ongoing_sends:
                d = self._ongoing_sends.pop()
                d.cancel()

        def close_connections(_):
            all_connections = [c for conns in self._connections.itervalues() for c in conns]
            
            logger.debug("Closing all connections (there are %s)..." % len(all_connections))
            for c in all_connections:
                c.transport.loseConnection()
            ds = [c.wait_for_close() for c in all_connections]
            d = defer.DeferredList(ds, fireOnOneErrback=True)
            
            def allclosed(_):
                logger.debug("All connections closed.")
            d.addCallback(allclosed)
            return d
        
        logger.debug("Closing connection pool...")
        
        d = defer.maybeDeferred(self._listeningport.stopListening)
        d.addCallback(cancel_sends)
        d.addCallback(close_connections)
        return d
    
    def _connection_made(self, protocol):
        peer = protocol.peer
        logger.debug("Connection established with %s" % peer)
        
        if peer in self._connections:
            self._connections[peer].append(protocol)
        else:
            self._connections[peer] = [protocol]
    
    def _connection_lost(self, protocol):
        peer = protocol.peer
        
        logger.debug("Lost connection to %s" % peer)
        
        connections = self._connections[peer]
        connections.remove(protocol)
        if not connections:
            del self._connections[peer]
    
class PoolProtocol(packetprotocol.PacketProtocol):
    
    HANDSHAKE = "PoolProtocol_handshake"
    
    def __init__(self, pool, ownid, peer=None):
        packetprotocol.PacketProtocol.__init__(self)
        self.pool = pool
        self.ownid = ownid
        self.peer = peer
        self.register_type(self.HANDSHAKE)
        
        self.handshake_completed = False
        self.handshake_deferred = defer.Deferred()
        
        def canceller(_):
            self.transport.loseConnection()
        
        self.closed_deferred = defer.Deferred(canceller)
        
    def wait_for_handshake(self):
        def canceller(_):
            self.handshake_deferred.cancel()
        d = defer.Deferred(canceller)
        self.handshake_deferred.chainDeferred(d)
        return d
        
    def wait_for_close(self):
        d = defer.Deferred()
        self.closed_deferred.chainDeferred(d)
        return d
        
    def connectionMade(self):
        packetprotocol.PacketProtocol.connectionMade(self)
        self.send_packet(self.HANDSHAKE, self.ownid)
        
    def connectionLost(self, reason=protocol.connectionDone):
        packetprotocol.PacketProtocol.connectionLost(self, reason=reason)
        if self.handshake_completed:
            self.pool._connection_lost(self)
        self.closed_deferred.callback(None)
        
    def packet_received(self, typename, packet):
        try:
            if typename == self.HANDSHAKE:
                peer = packet
                if self.peer and self.peer != peer:
                    raise ValueError("Peer says it is %s, but we expected %s. Closing connection." %(repr(peer), repr(self.peer)))
                else:
                    self.handshake_completed = True
                    self.peer = peer
                    self.pool._connection_made(self)
                    self.handshake_deferred.callback(None)
            elif not self.handshake_completed:
                raise ValueError("Expected handshake, got %s. Closing connection. "%repr(typename))
            else:
                self.pool.packet_received(self.peer, typename, packet)
        except ValueError:
            logger.exception("Error while receiving package")
            self.transport.loseConnection()
            self.handshake_deferred.errback()
    
class PoolFactory(protocol.Factory):

    def __init__(self, pool, typenames, peer=None):
        self.pool = pool
        self.typenames = typenames
        self.peer = peer
        
    def buildProtocol(self, addr):
        p = PoolProtocol(self.pool, self.pool.ownid, self.peer)
        for t in self.typenames:
            p.register_type(t)
        return p