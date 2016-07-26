import logging
import serial
import re
import sys
import asyncio

import artiq.protocols.pyon as pyon

logger = logging.getLogger(__name__)

class PiezoController:
    """Driver for Thorlabs MDT693B 3 channel open-loop piezo controller."""
    def __init__(self, serial_addr):
        if serial_addr is None:
            self.simulation = True
        else:
            self.simulation = False
            self.port = serial.Serial(
                serial_addr,
                baudrate=115200,
                timeout=0.1,
                write_timeout=0.1)

        self.echo = None
        self._purge()
        self._set_echo(False, verify=False)
        self.vLimit = self.get_voltage_limit()
        logger.info("Device vlimit is {}".format(self.vLimit))

        self.fname = "piezo_{}.pyon".format(self.get_serial())
        self.channels = {'x':-1, 'y':-1, 'z':-1}
        self._load_setpoints()

    def _purge(self):
        """Make sure we start from a clean slate with the controller"""
        if not self.simulation:
            self._send_command("", verify=False)
            logger.info("Clean slate established")

    def _load_setpoints(self):
        """Load setpoints from a file"""
        try:
            self.channels = pyon.load_file(self.fname)
            logger.info("Loaded '{}', channels: {}".format(self.fname, self.channels))
        except FileNotFoundError:
            logger.warning("Couldn't find '{}', no setpoints loaded".format(self.fname))

    def save_setpoints(self):
        """Save current set values to file"""
        pyon.store_file(self.fname, self.channels)
        logger.info("Saved '{}', channels: {}".format(self.fname, self.channels))

    def close(self):
        """Close the serial port."""
        if not self.simulation:
            self.port.close()

    def _send_command(self, cmd, verify=True):
        if self.simulation:
            print(cmd)
            return None
        else:
            try:
                self.port.write((cmd+'\r').encode())
            except serial.SerialTimeoutException as e:
                logger.exception("Serial write timeout: Force exit")
                # This is hacky but makes the server exit
                asyncio.get_event_loop().call_soon(sys.exit, 42)
                raise

            if self.echo:
                # Read off the echoed command to stay in sync
                _ = self._read_line()

            if verify:
                self._read_asterisk(cmd)
            else:
                self.port.reset_input_buffer()

    def _read_asterisk(self, cmd):
        """Read a single character after a command and check success"""
        c = self.port.read().decode()
        if c == '*':
            logger.debug('Command "{}" successful'.format(cmd))
        elif c == '!':
            raise ControllerError('Command "{}" failed'.format(cmd))
        else:
            raise ControllerError('Command "{}" failed, unexpectedly returned "{}"'.format(cmd, c))

    def _read_line(self):
        """Read a CR terminated line. Returns '' on timeout"""
        s = ''
        while len(s) == 0 or s[-1] != '\r':
            c = self.port.read().decode()
            if c == '': # Timeout
                break
            s += c
        return s

    def _read_bracketed(self):
        """Read a line with string enclosed in square brackets and return string"""
        line = self._read_line()
        match = re.search("\[(.*)\]", line)
        if match:
            return match.group(1)
        raise ParseError('Bracketed string not found in "{}"'.format(line))

    def _get_echo(self):
        """Get echo mode of controller"""
        self._send_command("echo?")
        self.echo = self._read_bracketed() == "Echo On"
        return self.echo

    def _set_echo(self, enable, verify=True):
        """Set echo mode of controller"""
        # NB "echo=" command is awful, in that it always elicits a response
        # of *[Echo On]\r* or *[Echo Off]\r* regardless, unlike all other set
        # commands which just set the value quietly
        self._send_command("echo={}".format(1 if enable else 0), verify)
        if verify:
            self.echo = self._read_bracketed() == "Echo On"
            self._read_asterisk("echo")
        else:
            self.echo = enable

    def get_serial(self):
        """Returns the device serial string."""
        id = self.get_id()
        match = re.search("Serial#:(.*)", id)
        if match:
            return match.group(1).strip()
        # If we get here we got a timeout
        raise IOError("Timeout while reading serial string")

    def get_id(self):
        """Returns the identity paragraph.

        This includes the device model, serial number, and firmware version. 
        This function needs to wait for a serial timeout, hence is a little 
        slow"""
        # Due to the crappy Thorlabs protocol (no clear finish marker) we have
        # to wait for a timeout to ensure that we have read everything
        self._send_command('id?')
        s = ''
        line = self._read_line()
        while line != '':
            s += line
            line = self._read_line()
        return s.replace('\r', '\n')

    def set_channel(self, channel, voltage):
        """Set a channel (one of 'x','y','z') to a given voltage."""
        self._check_valid_channel(channel)
        self._check_voltage_in_limit(voltage)
        self._send_command("{}voltage={}".format( channel, voltage))
        self.channels[channel] = voltage

    def get_channel_output(self, channel):
        """Returns the current *output* voltage for a given channel.

        Note that this may well differ from the set voltage by a few volts due
        to ADC and DAC offsets."""
        self._check_valid_channel(channel)
        self._send_command("{}voltage?".format(channel))
        return float( self._read_bracketed() )

    def get_channel(self, channel):
        """Return the last voltage set via USB for a given channel"""
        self._check_valid_channel(channel)
        return self.channels[channel]

    def get_voltage_limit(self):
        """Returns the output limit setting in Volts (one of 75V, 100V, 150V, set by
        the switch on the device back panel)"""
        str = self._send_command("vlimit?")
        return float( self._read_bracketed() )

    def _check_valid_channel(self, channel):
        """Raises a ValueError if the channel is not valid"""
        if channel not in self.channels:
            raise ValueError("Channel must be one of 'x', 'y', or 'z'")

    def _check_voltage_in_limit(self, voltage):
        """Raises a ValueError if the voltage is not in limit for the current
        controller settings"""
        if voltage > self.vLimit or voltage < 0:
            raise ValueError("Voltage must be between 0 and vlimit={}".format(self.vLimit))

    def ping(self):
        self.get_voltage_limit()
        return True

class ParseError(Exception):
    """Raised when controller output cannot be parse as expected"""

class ControllerError(Exception):
    """Raised when commands are not accepted by the controller"""
