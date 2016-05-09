import time
import logging
import socket

logger = logging.getLogger(__name__)


class RohdeSynth:

    def __init__(self, addr):
        # addr : IP address of synth
        self.addr = addr
        self.port = 5025
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.addr, self.port))
        logger.info("Connected to RohdeSynth with ID '{}'".format(self.identity()))
        self.sanity()

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

    def sanity(self):
        """
        Make sure the synth is set up sensibly.

        Offsets and multipliers don't actually affect the signal, but best to
        make sure that all offsets are 0 and multipliers 1 so that when we
        query values we get the actual value at the output.
        """
        self.send("FREQ:MODE FIX\n")
        self.send("FREQ:OFFS 0\n")
        self.send("FREQ:MULT 1\n")

        self.send("POW:MODE FIX\n")
        self.send("POW:OFFS 0\n")


    def setFrequency(self, frequency):
        """Set frequency in Hz"""
        if frequency < 9e3 or frequency > 3e9:
            msg = "Frequency '{}' invalid: should be a float between 9kHz and 3GHz"
            raise ValueError(msg.format(frequency))

        self.send("FREQ {}\n".format(frequency))

    def frequency(self):
        """Query frequency in Hz"""
        return float(self.query("FREQ?\n"))


    def setPower(self, power):
        """Set power level in dBm. Limited to +5 dBm by choice not instrument"""
        if power < -120 or power > 5:
            msg = "Power '{}' invalid: should be a float between -120dBm and +5dBm"
            raise ValueError(msg.format(power))

        self.send("POW {}\n".format(power))

    def power(self):
        """Query power in dBm"""
        return float(self.query("POW?\n"))
        
    def identity(self):
        return self.query("*IDN?\n")

    def ping(self):
        return True


class RohdeSynthSim:
    def setFrequency(self, frequency):
        pass

    def frequency(self):
        return 666e6

    def setPower(self, power):
        pass

    def power(self):
        return -42

    def close(self):
        pass

    def ping(self):
        return True
