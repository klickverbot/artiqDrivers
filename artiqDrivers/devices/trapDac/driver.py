import logging
import serial
import time
import math


logger = logging.getLogger(__name__)



class TrapDac:
    def __init__(self, addr_dc_iface=None, addr_rf_iface=None):
        self.dc_iface = OldlabDCInterface(addr_dc_iface)
        self.rf_iface = OldlabRFAttenuatorInterface(addr_rf_iface)

        self.rf_level = -14
        self.dc_vec = [0]*5

    def set_rf_level(self, rf_level):
        """Set the RF level in dB.
        Valid range -31.5 to 0"""
        self.rf_iface.set_atten(-rf_level)
        self.rf_level = rf_level

    def get_rf_level(self):
        """Returns the RF level in dB"""
        return self.rf_level

    def set_dc(self, dc_vec):
        """Set all 5 dc channels simultaneously"""
        self.dc_iface.set_all_dac_channels(*dc_vec)
        self.dc_vec = dc_vec

    def get_dc(self):
        """Returns the DC vector"""
        return self.dc_vec

    def ping(self):
        return True


class OldlabDCInterface:
    def __init__(self, addr):
        self.ser = serial.Serial(addr, baudrate=115200)
        time.sleep(2)
    
    def set_dac_channel(self, channel=0, value=0): 
        """Sets a given DAC channel to a given value in Volts"""
        assert(channel>=0)
        assert(channel<5)

        self.ser.write('v {} {:3.3f}\n'.format(channel,value).encode())

    def set_all_dac_channels(self, ch0, ch1, ch2, ch3, ch4): 
        """Simultaneously set all DAC channels"""
        self.ser.write('va {:3.3f} {:3.3f} {:3.3f} {:3.3f} {:3.3f}\n'.format(ch0, ch1, ch2, ch3, ch4).encode())


class OldlabRFAttenuatorInterface:
    def __init__(self, addr):
        self.ser = serial.Serial(addr, baudrate=115200)
        time.sleep(2)
    
    def set_atten(self, value=0):
        """Set the attenutation in dB"""
        atten = math.floor( value*2 + 0.5)/2.0
        atten = min(atten,31.5)
        atten = max(atten,0)
        attenLSB = int(atten/0.5) # Attenutation value in hardware units of 0.5dB
        self.ser.write('atten {}\n'.format(attenLSB).encode())
