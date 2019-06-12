Adafruit_Python_MAX31856
========================

Python library for accessing the MAX31856 thermocouple temperature sensor on a Raspberry Pi.

Designed specifically to work with the `Adafruit MAX31856 sensor <https://www.adafruit.com/products/3263>`_.

Installing dependencies
-----------------------
Run the following:

.. code::

    $ sudo apt-get update
    $ sudo apt-get install build-essential python-dev python-smbus

Make Sure SPI is Enabled on Your Pi
-----------------------------------

To enable SPI, edit the /boot/config.txt file, uncommenting the line about SPI, and setting it to: dtparam=spi=on

You can confirm that SPI is enabled by checking to see you get a response similar to the one below.

.. code::

    $ lsmod | grep spi
    spi_bcm2835     7074  0

Installing Library
------------------

I recommend running this code from within a virtual environment, cd to your desired source directory and clone the
repository:

.. code::

    $ git clone https://github.com/johnrbnsn/Adafruit_Python_MAX31856.git
    $ cd Adafruit_Python_MAX31856
    $ python3 -m venv env_py3
    $ source env_py3/bin/activate
    (env_py3) $ pip install -r requirements.txt
    (env_py3) $ pip install ./.

Running Example/ Tests
----------------------

Examples are in the examples directory, or tests are in the
`Adafruit_MAX31856 <https://github.com/johnrbnsn/Adafruit_Python_MAX31856/tree/master/Adafruit_MAX31856>`_
directory.  From within this directory, run simpletest.py, or the same example with an alternate thermocouple type (k
for the example, same process for any thermocouple type):

.. code::

    (env_py3) $ python simpletest.py
    (env_py3) $ python simpletest_k_type.py

Runing Tests, cd to
`Adafruit_MAX31856 <https://github.com/johnrbnsn/Adafruit_Python_MAX31856/tree/master/Adafruit_MAX31856>`_
and run:

.. code::

    (env_py3) $ python test_MAX31856.py -v

Debugging
---------

If you are having issues, run the tests located in the
`Adafruit\_MAX31856 <https://github.com/johnrbnsn/Adafruit_Python_MAX31856/tree/master/Adafruit_MAX31856>`_
directory by:

.. code::

    python test_MAX31856.py -v

The resulting output and the test_MAX31856.log file should help with debugging the issue.

Acknowledgement
---------------
This code was modeled after the
`Adafruit MAX31855 repository <https://github.com/adafruit/Adafruit_Python_MAX31855>`_ which works with
the prior version of this thermocouple amplifier.  There is only an Arduino example available from Adafruit at this
time, since I use RasPi, I created this library.
