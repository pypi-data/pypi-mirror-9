#!/usr/bin/env python2.7

import socket, struct, ssl, time, collections
from packets import *

class TCPConnection(object):

    __eof = "\r\n"
    __connections = {}
    
    @staticmethod
    def get_connection(address):
    
        try: return TCPConnection.__connections[address]
        except: return None
    
    @staticmethod
    def get_connections():
    
        return TCPConnection.__connections.values()
    
    @staticmethod
    def remove_connection(address):

        try: return TCPConnection.__connections.pop(address)
        except: return None

    def __init__(self, (sock, address)):
    
        self._socket = sock
        self._address = address
        
        self._queue = collections.deque()
        
        self._identified = False
        
        TCPConnection.__connections.update({ self.get_address() : self })

    def fileno(self):
    
        return self._socket.fileno()

    def get_address(self):
    
        return "%s:%s" % (self._address)

    def send_next(self):
    
        try:
            res = [self._socket.send(data) for data in [self._queue.popleft() for count in xrange(0, 1)]]
            if 0 in res:
                TCPConnection.remove_connection(self.get_address())
        except (IndexError) as e: pass
        except: raise

    def send(self, data, now = False):
    
        data = self.connection_send_pre(data)

        if now:
            self._socket.send(data)
        else:
            self._queue.append(data)

        self.connection_send_post(data)
    
    def read_next(self):
    
        data = self._socket.recv(4096).split(TCPConnection.__eof)
        data.pop(len(data) - 1) # pop empty garbage data left over from splitting __eof
        for raw in data:
            packet = packets.match_packet(raw)
            if packet: self.connection_recv_packet(packet)
            else: self.connection_recv_data(raw)

    def connection_recv_packet(self, packet):

        pass

    def connection_recv_data(self, data):

        pass

    def connection_send_pre(self, data):

        pass

    def connection_send_post(self, data):

        pass
