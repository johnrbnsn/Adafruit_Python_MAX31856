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
import Adafruit_GPIO.SPI as SPI

# Local Imports
from max31856 import MAX31856 as MAX31856

logging.basicConfig(filename='test_MAX31856.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

class Adafruit_MAX31856(unittest.TestCase):
    
    def test_hardware_SPI_initialize(self):
        '''Checks to see if the sensor can initialize on the hardware SPI interface.
        
        Will fail if it cannot find the MAX31856 library or any dependencies.
        Test only checks to see that the sensor can be initialized in Software, does not check the hardware connection.
        '''
        _logger.debug('test_hardware_SPI_initialize()')
        # Raspberry Pi hardware SPI configuration.
        SPI_PORT   = 0
        SPI_DEVICE = 0
        sensor = MAX31856(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
        
        if sensor:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
            
    def test_get_register_reading(self):
        '''Checks to see if we can read a register from the device.  Good test for correct connectivity.
        '''
        _logger.debug('test_get_register_reading()')
        # Raspberry Pi hardware SPI configuration.
        SPI_PORT   = 0
        SPI_DEVICE = 0
        sensor = MAX31856(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
        
        value = sensor._read_register(MAX31856.MAX31856_REG_READ_CR0)
        for ii in range(0x00, 0x10):
            # Read all of the registers, will store data to log
            sensor._read_register(ii)
        
        if value:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_get_temperaure_reading(self):
        '''Checks to see if we can read a temperature from the board, using Hardware SPI
        '''
        _logger.debug('test_get_temperature_reading')
        # Raspberry Pi hardware SPI configuration.
        SPI_PORT   = 0
        SPI_DEVICE = 0
        sensor = MAX31856(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
        
        temp = sensor.readTempC()

        if temp:
            self.assertTrue(True)
        else:
            self.assertTrue(False)


    def test_get_internal_temperaure_reading(self):
        '''Checks to see if we can read a temperature from the board, using Hardware SPI
        '''
        _logger.debug('test_get_internal_temperature_reading()')
        # Raspberry Pi hardware SPI configuration.
        SPI_PORT   = 0
        SPI_DEVICE = 0
        sensor = MAX31856(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

        temp = sensor.readInternalTempC()

        if temp:
            self.assertTrue(True)
        else:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
