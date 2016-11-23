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
    
    ### Register constants, see data sheet Table 6 (in Rev. 0) for info.
    # Read Addresses
    MAX31856_REG_READ_CR0 = 0x00   
    MAX31856_REG_READ_CR1 = 0x01
    MAX31856_REG_READ_MASK = 0x02
    MAX31856_REG_READ_CJHF = 0x03
    MAX31856_REG_READ_LTCBL = 0x0E # Linearized TC Temperature, Byte 0
    MAX31856_REG_READ_LTCBM = 0x0D
    MAX31856_REG_READ_LTCBH = 0x0C
    MAX31856_REG_READ_CJTL = 0x0B  # Cold-Junction Temperature Register, LSB
    MAX31856_REG_READ_CJTH = 0x0A  # Cold-Junction Temperature Register, MSB
    
    # Write Addresses
    MAX31856_REG_WRITE_CR0 = 0x80
    MAX31856_REG_WRITE_CR1 = 0x81

    # Pre-config Register Options
    MAX31856_CR0_READ_ONE = 0x40 # One shot reading, delay approx. 200ms then read temp registers
    MAX31856_CR0_READ_CONT = 0x80 # Continuous reading, delay approx. 100ms between readings
    
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
        #                                        + val_low_byte )*value of LSB
        temp_C = ( ((val_high_byte & 0x7F) << 6) + val_low_byte )*2**-6
        
        if val_high_byte & 0x80:
            # Negative Value.  
            temp_C = -1.0*temp_C
            
        self._logger.debug("Cold Junction Temperature {0} deg. C".format(temp_C))
        
        return temp_C
    

    def readTempC(self):
        """Return the thermocouple temperature value in degrees celsius."""
        val_low_byte = self._read_register(self.MAX31856_REG_READ_LTCBL)
        val_mid_byte = self._read_register(self.MAX31856_REG_READ_LTCBM)
        val_high_byte = self._read_register(self.MAX31856_REG_READ_LTCBH)
            
        #        ( ((val_high_byte w/o +/-) shifted by number of bits above LSB)
        #                                         + (val_mid_byte shifted by number of bits above LSB)
        #                                                               + val_low_byte )*value of LSB
        temp_C = ( ((val_high_byte & 0x7F) << 11) + (val_mid_byte << 3) + val_low_byte )*2**-7

        if val_high_byte & 0x80:
            # Negative Value.  
            temp_C = -1.0*temp_C
        
        self._logger.debug("Thermocouple Temperature {0} deg. C".format(temp_C))
        
        return temp_C

    #def readState(self):
        #"""Return dictionary containing fault codes and hardware problems
        #"""
        #v = self._read32()
        #return {
            #'openCircuit': (v & (1 << 0)) > 0,
            #'shortGND': (v & (1 << 1)) > 0,
            #'shortVCC': (v & (1 << 2)) > 0,
            #'fault': (v & (1 << 16)) > 0
        #}

    #def readLinearizedTempC(self):
        #"""Return the NIST-linearized thermocouple temperature value in degrees celsius.
        #See https://learn.adafruit.com/calibrating-sensors/maxim-31855-linearization for more info.
        #"""
        ## MAX31855 thermocouple voltage reading in mV
        #thermocoupleVoltage = (self.readTempC() - self.readInternalC()) * 0.041276
        ## MAX31855 cold junction voltage reading in mV
        #coldJunctionTemperature = self.readInternalC()
        #coldJunctionVoltage = (-0.176004136860E-01 +
            #0.389212049750E-01  * coldJunctionTemperature +
            #0.185587700320E-04  * math.pow(coldJunctionTemperature, 2.0) +
            #-0.994575928740E-07 * math.pow(coldJunctionTemperature, 3.0) +
            #0.318409457190E-09  * math.pow(coldJunctionTemperature, 4.0) +
            #-0.560728448890E-12 * math.pow(coldJunctionTemperature, 5.0) +
            #0.560750590590E-15  * math.pow(coldJunctionTemperature, 6.0) +
            #-0.320207200030E-18 * math.pow(coldJunctionTemperature, 7.0) +
            #0.971511471520E-22  * math.pow(coldJunctionTemperature, 8.0) +
            #-0.121047212750E-25 * math.pow(coldJunctionTemperature, 9.0) +
            #0.118597600000E+00  * math.exp(-0.118343200000E-03 * math.pow((coldJunctionTemperature-0.126968600000E+03), 2.0)))
        ## cold junction voltage + thermocouple voltage
        #voltageSum = thermocoupleVoltage + coldJunctionVoltage
        ## calculate corrected temperature reading based on coefficients for 3 different ranges
        ## float b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10;
        #if thermocoupleVoltage < 0:
            #b0 = 0.0000000E+00
            #b1 = 2.5173462E+01
            #b2 = -1.1662878E+00
            #b3 = -1.0833638E+00
            #b4 = -8.9773540E-01
            #b5 = -3.7342377E-01
            #b6 = -8.6632643E-02
            #b7 = -1.0450598E-02
            #b8 = -5.1920577E-04
            #b9 = 0.0000000E+00
        #elif thermocoupleVoltage < 20.644:
            #b0 = 0.000000E+00
            #b1 = 2.508355E+01
            #b2 = 7.860106E-02
            #b3 = -2.503131E-01
            #b4 = 8.315270E-02
            #b5 = -1.228034E-02
            #b6 = 9.804036E-04
            #b7 = -4.413030E-05
            #b8 = 1.057734E-06
            #b9 = -1.052755E-08
        #elif thermocoupleVoltage < 54.886:
            #b0 = -1.318058E+02
            #b1 = 4.830222E+01
            #b2 = -1.646031E+00
            #b3 = 5.464731E-02
            #b4 = -9.650715E-04
            #b5 = 8.802193E-06
            #b6 = -3.110810E-08
            #b7 = 0.000000E+00
            #b8 = 0.000000E+00
            #b9 = 0.000000E+00
        #else:
            ## TODO: handle error - out of range
            #return 0
        #return (b0 +
            #b1 * voltageSum +
            #b2 * pow(voltageSum, 2.0) +
            #b3 * pow(voltageSum, 3.0) +
            #b4 * pow(voltageSum, 4.0) +
            #b5 * pow(voltageSum, 5.0) +
            #b6 * pow(voltageSum, 6.0) +
            #b7 * pow(voltageSum, 7.0) +
            #b8 * pow(voltageSum, 8.0) +
            #b9 * pow(voltageSum, 9.0))
            
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
    
    
