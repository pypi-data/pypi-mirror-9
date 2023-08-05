#!/usr/bin/env python2.7
import struct, time, hmac

__packets__ = ['DataPacket']

def match_packet(data):

    get_class = lambda cls: globals()[cls]
    for packet in __packets__:
        try:
            packet = get_class(packet)
            p = packet()
            p.fromstr(data.split(DataPacket.__eop)[0])
            return p
        except (struct.error) as e: continue

def match_packets(data):

    for packet in data.split(DataPacket.__eop):
        yield match_packet(packet)

def register_packet(clsname):

    try: get_class(clsname)
    except: return

    __packets__.append(clsname)

class DataPacket(object):

    __eop = "\r\n"
    
    def __init__(self):
    
        self._format = ">i"
        
        self._pack = ['id']
    
        self.id = -1
        
    def fromstr(self, data):
    
        try:
            vals = self.unpack(data)
            ind = self._pack.index('id')
            if vals[ind] != self.id:
                raise struct.error("Packet id %s does not match my id %s" % (vals[ind], self.id))
            if len(vals) == len(self._pack):
                for var in self._pack:
                    setattr(self, var, vals[self._pack.index(var)])
                return vals
            else:
                raise struct.error("Data indexes do not match pack indexes.")
        except (struct.error) as e: raise
    def pack(self):
    
        vals = []
        for var in self._pack:
            vals.append(getattr(self, var))
        return struct.pack(self._format, *vals) + DataPacket.__eop
    
    def unpack(self, data):
    
        try: return struct.unpack(self._format, data)
        except (struct.error) as e: raise
        except: return None
