# Copyright (c) 2016 John Robinson
# Author: John Robinson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging
import math

import Adafruit_GPIO as Adafruit_GPIO
import Adafruit_GPIO.SPI as SPI


class MAX31856(object):
    """Class to represent an Adafruit MAX31856 thermocouple temperature
    measurement board.
    """
    
    # Board Specific Constants
    MAX31856_CONST_THERM_LSB = 2**-7
    MAX31856_CONST_THERM_BITS = 19
    MAX31856_CONST_CJ_LSB = 2**-6
    MAX31856_CONST_CJ_BITS = 14
    
    ### Register constants, see data sheet Table 6 (in Rev. 0) for info.
    # Read Addresses
    MAX31856_REG_READ_CR0 = 0x00
    MAX31856_REG_READ_CR1 = 0x01
    MAX31856_REG_READ_MASK = 0x02
    MAX31856_REG_READ_CJHF = 0x03
    MAX31856_REG_READ_CJLF = 0x04
    MAX31856_REG_READ_LTHFTH = 0x05
    MAX31856_REG_READ_LTHFTL = 0x06
    MAX31856_REG_READ_LTLFTH = 0x07
    MAX31856_REG_READ_LTLFTL = 0x08
    MAX31856_REG_READ_CJTO = 0x09
    MAX31856_REG_READ_CJTH = 0x0A  # Cold-Junction Temperature Register, MSB
    MAX31856_REG_READ_CJTL = 0x0B  # Cold-Junction Temperature Register, LSB
    MAX31856_REG_READ_LTCBH = 0x0C # Linearized TC Temperature, Byte 2
    MAX31856_REG_READ_LTCBM = 0x0D # Linearized TC Temperature, Byte 1
    MAX31856_REG_READ_LTCBL = 0x0E # Linearized TC Temperature, Byte 0
    MAX31856_REG_READ_FAULT = 0x0F # Fault status register
    
    # Write Addresses
    MAX31856_REG_WRITE_CR0 = 0x80
    MAX31856_REG_WRITE_CR1 = 0x81
    MAX31856_REG_WRITE_MASK = 0x82
    MAX31856_REG_WRITE_CJHF = 0x83
    MAX31856_REG_WRITE_CJLF = 0x84
    MAX31856_REG_WRITE_LTHFTH = 0x85
    MAX31856_REG_WRITE_LTHFTL = 0x86
    MAX31856_REG_WRITE_LTLFTH = 0x87
    MAX31856_REG_WRITE_LTLFTL = 0x88
    MAX31856_REG_WRITE_CJTO = 0x89
    MAX31856_REG_WRITE_CJTH = 0x8A  # Cold-Junction Temperature Register, MSB
    MAX31856_REG_WRITE_CJTL = 0x8B  # Cold-Junction Temperature Register, LSB
    
    # Pre-config Register Options
    MAX31856_CR0_READ_ONE = 0x40 # One shot reading, delay approx. 200ms then read temp registers
    MAX31856_CR0_READ_CONT = 0x80 # Continuous reading, delay approx. 100ms between readings
    
    # Thermocouple Types
    MAX31856_B_TYPE = 0x0 # Read B Type Thermocouple
    MAX31856_E_TYPE = 0x1 # Read E Type Thermocouple
    MAX31856_J_TYPE = 0x2 # Read J Type Thermocouple
    MAX31856_K_TYPE = 0x3 # Read K Type Thermocouple
    MAX31856_N_TYPE = 0x4 # Read N Type Thermocouple
    MAX31856_R_TYPE = 0x5 # Read R Type Thermocouple
    MAX31856_S_TYPE = 0x6 # Read S Type Thermocouple
    MAX31856_T_TYPE = 0x7 # Read T Type Thermocouple
    
    
    def __init__(self, tc_type=MAX31856_T_TYPE, avgsel=0x0, clk=None, cs=None, do=None, di=None, spi=None):
        """Initialize MAX31856 device with software SPI on the specified CLK,
        CS, and DO pins.  Alternatively can specify hardware SPI by sending an
        Adafruit_GPIO.SPI.SpiDev device in the spi parameter.
        
        Args:
            tc_type (1-byte Hex): Type of Thermocouple.  Choose from class variables of the form MAX31856.MAX31856_X_TYPE.
            avgsel (1-byte Hex): Type of Averaging.  Choose from values in CR0 table of datasheet.  Default is single sample.
            clk (integer): Pin number for software SPI clk
            cs (integer): Pin number for software SPI cs
            do (integer): Pin number for software SPI MISO
            di (integer): Pin number for software SPI MOSI
            spi (Adafruit_GPIO.SPI.SpiDev): If using hardware SPI, define the connection
        """
        self._logger = logging.getLogger('Adafruit_MAX31856.MAX31856')
        self._spi = None
        self.tc_type = tc_type
        self.avgsel = avgsel
        # Handle hardware SPI
        if spi is not None:
            self._logger.debug('Using hardware SPI')
            self._spi = spi
        elif clk is not None and cs is not None and do is not None:
            self._logger.debug('Using software SPI')
            # Default to platform GPIO if not provided.
            if gpio is None:
                gpio = GPIO.get_platform_gpio()
            self._spi = SPI.BitBang(gpio, clk, None, do, cs)
        else:
            raise ValueError('Must specify either spi for for hardware SPI or clk, cs, and do for softwrare SPI!')
        self._spi.set_clock_hz(5000000)
        self._spi.set_mode(1) # According to Wikipedia (on SPI) and MAX31856 Datasheet, SPI mode 0 corresponds with correct timing, CPOL = 0, CPHA = 1
        self._spi.set_bit_order(SPI.MSBFIRST)
        
        self.CR1 = ((self.avgsel << 1) + self.tc_type)

        # Setup for reading continuously with T-Type thermocouple 
        self._write_register(self.MAX31856_REG_WRITE_CR0, self.MAX31856_CR0_READ_CONT)
        self._write_register(self.MAX31856_REG_WRITE_CR1, self.CR1)
    
    
    def readInternalTempC(self):
        """Return internal temperature value in degrees celsius."""
        val_low_byte = self._read_register(self.MAX31856_REG_READ_CJTL)
        val_high_byte = self._read_register(self.MAX31856_REG_READ_CJTH)
        
        #        ( ((val_high_byte w/o +/-) shifted by number of bits above LSB)
        #                                            + val_low_byte )
        temp_bytes = ( ((val_high_byte & 0x7F) << 6) + val_low_byte )
        
        if val_high_byte & 0x80:
            # Negative Value.  Scale back by number of bits
            temp_bytes -= 2**self.MAX31856_CONST_CJ_BITS
        
        #        temp_bytes*value of LSB
        temp_C = temp_bytes*self.MAX31856_CONST_CJ_LSB
        self._logger.debug("Cold Junction Temperature {0} deg. C".format(temp_C))
        
        return temp_C
    
    
    def readTempC(self):
        """Return the thermocouple temperature value in degrees celsius."""
        val_low_byte = self._read_register(self.MAX31856_REG_READ_LTCBL)
        val_mid_byte = self._read_register(self.MAX31856_REG_READ_LTCBM)
        val_high_byte = self._read_register(self.MAX31856_REG_READ_LTCBH)
        
        #            ( ((val_high_byte w/o +/-) shifted by number of bits above LSB)
        #                                             + (val_mid_byte shifted by number of bits above LSB)
        #                                                                   + val_low_byte )
        temp_bytes = ( ((val_high_byte & 0x7F) << 11) + (val_mid_byte << 3) + val_low_byte )
        
        if val_high_byte & 0x80:
            # Negative Value.  Scale back by number of bits
            temp_bytes -= 2**self.MAX31856_CONST_THERM_BITS
        
        #        temp_bytes*value of LSB
        temp_C = temp_bytes*self.MAX31856_CONST_THERM_LSB
        
        self._logger.debug("Thermocouple Temperature {0} deg. C".format(temp_C))
        
        return temp_C
    
    
    def read_fault_register(self):
        """Return bytes containing fault codes and hardware problems.  
        
        TODO: Could update in the future to return human readable values
        """
        v = self._read_register(self.MAX31856_REG_READ_FAULT)
        return v
    
    
    def _read_register(self, address):
        '''Reads a register at address from the MAX31856
        
        Args:
            address (8-bit Hex): Address for read register.  Format 0Xh. Constants listed in class as MAX31856_REG_READ_*
            
        Note:
            SPI transfer method is used.  The address is written in as the first byte, and then a dummy value as the second byte.
            The data from the sensor is contained in the second byte, the dummy byte is only used to keep the SPI clock ticking as 
            we read in the value.  The first returned byte is discarded because no data is transmitted while specifying the register
            address.
        '''
        
        raw = self._spi.transfer([address, 0x00])
        if raw is None or len(raw) != 2:
            raise RuntimeError('Did not read expected number of bytes from device!')
        
        value = raw[1]
        self._logger.debug('Read Register: 0x{0:02X}, Raw Value: 0x{1:02X}'.format( (address & 0xFFFF), (value & 0xFFFF) ))
        return value
    
    
    def _write_register(self, address, write_value):
        '''Writes to a register at address from the MAX31856
        
        Args:
            address (8-bit Hex): Address for read register.  Format 0Xh. Constants listed in class as MAX31856_REG_WRITE_*
            write_value (8-bit Hex): Value to write to the register
        '''
        self._spi.transfer([address, write_value])
        self._logger.debug('Wrote Register: 0x{0:02X}, Value 0x{1:02X}'.format( (address & 0xFF), (write_value & 0xFF) ) )
        
        return True # If we've gotten this far without an exception, the transmission must've gone through
    
    
