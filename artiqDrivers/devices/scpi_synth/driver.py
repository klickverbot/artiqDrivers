import time
import logging
import socket

logger = logging.getLogger(__name__)


class ScpiSynth:

    def __init__(self, addr, port=5025):
        # addr : IP address of synth
        self.addr = addr
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.addr, port))

    def close(self):
        self.sock.close()
        self.sock = None

    def send(self, data):
        self.sock.send(data.encode())

    def query(self, data):
        self.send(data)
        with self.sock.makefile() as f:
            response = f.readline().strip()
        return response

    def set_frequency(self, frequency):
        """Set frequency in Hz"""
        self.send("FREQ {}\n".format(frequency))

    def set_amplitude(self, power):
        """Set output amplitude"""
        self.send("VOLT {}\n".format(power))
        
    def set_output(self, enable):
        if enable:
            en_str = "ON"
        else:
            en_str = "OFF"
        self.send("OUTP {}\n".format(en_str))
        
    def identity(self):
        return self.query("*IDN?\n")

    def ping(self):
        self.identity()
        return True
