#!/usr/bin/env python2.7

import socket, ssl, select, collections, time
from connection import TCPConnection

class TCPServer(object):

    __instance = None
    
    @staticmethod
    def get_instance():
    
        return TCPServer.__instance

    def __init__(self, host, port, ssl_enabled = False, ssl_keyfile = None, ssl_certfile = None):
        
        self._host = host
        self._port = port
        
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self._shutdown = False
        
        if ssl_enabled:
            if not ssl_keyfile or not ssl_certfile:
                ssl_enabled = False
            else:
                self._socket = ssl.wrap_socket(self._socket, keyfile = self._ssl_keyfile, certfile = self._ssl_certfile)
        
        self._connections = []
        self._queue = collections.deque()
    
    def listen(self, backlog = 10):
    
        try:
            self._socket.bind((self._host, self._port))
            self._socket.listen(backlog)
        except (Exception) as e:
            self.server_uncaptured_exception(e)
    
    def run(self):
    
        while not self._shutdown:
            time.sleep(0.001)

            try:
                r, w, e = select.select([self._socket], [], [self._socket], 0.5)
                if self._socket in r:
                    client = TCPConnection(self._socket.accept())
                    self.client_connection_opened(client)

                if self._socket in e:
                    self.server_poll_error()
                    self._shutdown = True

                r, w, e = select.select(TCPConnection.get_connections(), [], [], 0.5)

                for connection in r:
                    try:
                        connection.read_next()
                        self.client_connection_read(self, connection)
                    except (socket.error) as e:
                        self.client_connection_lost(connection)
                        TCPConnection.remove_connection(connection.get_address())

                for connection in TCPConnection.get_connections():
                    connection.send_next()
            except (KeyboardInterrupt, SystemExit) as e:
                self._shutdown = True
            except (Exception) as e:
                self.server_uncaptured_exception(e)
        
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def client_connection_lost(self, connection):

        pass

    def client_connection_opened(self, connection):

        pass

    def client_connection_read(self, connection):

        pass

    def server_uncaptured_exception(self, exc):

        pass

    def server_poll_error(self):

        pass
