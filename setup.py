try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup, find_packages

setup(name              = 'MAX31856',
      version           = '0.0.1',
      author            = 'John Robinson',
      author_email      = 'john.rbnsn@gmail.com',
      description       = 'Library for accessing the MAX31856 thermocouple temperature sensor on a Raspberry Pi.',
      license           = 'MIT',
      url               = 'https://github.com/johnrbnsn/Adafruit_Python_MAX31856/',
      dependency_links  = ['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5'],
      install_requires  = ['Adafruit-GPIO>=0.6.5'],
      packages          = find_packages())
