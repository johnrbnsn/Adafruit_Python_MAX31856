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

# Global Imports
import logging
import unittest
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

# Local Imports
from max31856 import MAX31856 as MAX31856

logging.basicConfig(filename='test_MAX31856.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

class Adafruit_MAX31856(unittest.TestCase):
    
    def tearDown(self):
        GPIO.cleanup()

    #def test_software_spi_initialize(self):
        #'''Checks to see if the sensor can initialize on the software SPI interface.

        #Will fail if it cannot find the MAX31856 library or any dependencies.
        #Test only checks to see that the sensor can be initialized in Software, does not check the
        #hardware connection.
        #'''
        #_logger.debug('test_software_SPI_initialize()')
        ## Raspberry Pi software SPI configuration.
        #software_spi = {"clk": 25, "cs": 8, "do": 9, "di": 10}
        #sensor = MAX31856(software_spi=software_spi)

        #if sensor:
            #self.assertTrue(True)
        #else:
            #self.assertTrue(False)

    def test_hardware_spi_initialize(self):
        '''Checks to see if the sensor can initialize on the hardware SPI interface.

        Will fail if it cannot find the MAX31856 library or any dependencies.
        Test only checks to see that the sensor can be initialized in Software, does not check the
        hardware connection.
        '''
        _logger.debug('test_hardware_SPI_initialize()')
        # Raspberry Pi hardware SPI configuration.
        spi_port = 0
        spi_device = 0
        sensor = MAX31856(hardware_spi=SPI.SpiDev(spi_port, spi_device))

        if sensor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_get_register_reading(self):
        '''Checks to see if we can read a register from the device.  Good test for correct
        connectivity.
        '''
        _logger.debug('test_get_register_reading()')
        # Raspberry Pi hardware SPI configuration.
        spi_port = 0
        spi_device = 0
        sensor = MAX31856(hardware_spi=SPI.SpiDev(spi_port, spi_device))

        value = sensor._read_register(MAX31856.MAX31856_REG_READ_CR0)
        for ii in range(0x00, 0x10):
            # Read all of the registers, will store data to log
            sensor._read_register(ii) # pylint: disable-msg=protected-access

        if value:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    #def test_get_temperaure_reading_software_spi(self):
        #'''Checks to see if we can read a temperature from the board, using software SPI
        #'''
        #_logger.debug('test_get_temperature_reading_software_spi')
        ## Raspberry Pi software SPI configuration.
        #software_spi = {"clk": 25, "cs": 8, "do": 9, "di": 10}
        #sensor = MAX31856(software_spi=software_spi)

        #temp = sensor.read_temp_c()

        #if temp:
            #self.assertTrue(True)
        #else:
            #self.assertTrue(False)

    def test_get_temperaure_reading(self):
        '''Checks to see if we can read a temperature from the board, using Hardware SPI
        '''
        _logger.debug('test_get_temperaure_reading')
        # Raspberry Pi hardware SPI configuration.
        spi_port = 0
        spi_device = 0
        sensor = MAX31856(hardware_spi=SPI.SpiDev(spi_port, spi_device))

        temp = sensor.read_temp_c()

        if temp:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
            
    def test_get_internal_temperaure_reading(self):
        '''Checks to see if we can read a temperature from the board, using Hardware SPI
        '''
        _logger.debug('test_get_internal_temperature_reading()')
        # Raspberry Pi hardware SPI configuration.
        spi_port = 0
        spi_device = 0
        sensor = MAX31856(hardware_spi=SPI.SpiDev(spi_port, spi_device))

        temp = sensor.read_internal_temp_c()

        if temp:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_temperature_byte_conversions(self):
        '''Checks the byte conversion for various known temperature byte values.
        '''
        _logger.debug('test_temperature_byte_conversions()')

        #-------------------------------------------#
        # Test Thermocouple Temperature Conversions #
        byte2 = 0x01
        byte1 = 0x70
        byte0 = 0x20
        decimal_temp = MAX31856._thermocouple_temp_from_bytes(byte0, byte1, byte2)  # pylint: disable-msg=protected-access
        self.assertEqual(decimal_temp, 23.0078125)

        # Check a couple values from the datasheet
        byte2 = 0b00000001
        byte1 = 0b10010000
        byte0 = 0b00000000
        decimal_temp = MAX31856._thermocouple_temp_from_bytes(byte0, byte1, byte2) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_temp, 25.0)

        byte2 = 0b00000000
        byte1 = 0b00000000
        byte0 = 0b00000000
        decimal_temp = MAX31856._thermocouple_temp_from_bytes(byte0, byte1, byte2) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_temp, 0.0)

        byte2 = 0b11111111
        byte1 = 0b11110000
        byte0 = 0b00000000
        decimal_temp = MAX31856._thermocouple_temp_from_bytes(byte0, byte1, byte2) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_temp, -1.0)

        byte2 = 0b11110000
        byte1 = 0b01100000
        byte0 = 0b00000000
        decimal_temp = MAX31856._thermocouple_temp_from_bytes(byte0, byte1, byte2) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_temp, -250.0)

        #---------------------------------#
        # Test CJ Temperature Conversions #
        msb = 0x1C
        lsb = 0x64
        decimal_cj_temp = MAX31856._cj_temp_from_bytes(msb, lsb) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_cj_temp, 28.390625)

        # Check a couple values from the datasheet
        msb = 0b01111111
        lsb = 0b11111100
        decimal_cj_temp = MAX31856._cj_temp_from_bytes(msb, lsb) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_cj_temp, 127.984375)

        msb = 0b00011001
        lsb = 0b00000000
        decimal_cj_temp = MAX31856._cj_temp_from_bytes(msb, lsb) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_cj_temp, 25)

        msb = 0b00000000
        lsb = 0b00000000
        decimal_cj_temp = MAX31856._cj_temp_from_bytes(msb, lsb) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_cj_temp, 0)

        msb = 0b11100111
        lsb = 0b00000000
        decimal_cj_temp = MAX31856._cj_temp_from_bytes(msb, lsb) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_cj_temp, -25)

        msb = 0b11001001
        lsb = 0b00000000
        decimal_cj_temp = MAX31856._cj_temp_from_bytes(msb, lsb) # pylint: disable-msg=protected-access
        self.assertEqual(decimal_cj_temp, -55)


if __name__ == "__main__":
    unittest.main()
