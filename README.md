Adafruit_Python_MAX31856
========================

Python library for accessing the MAX31856 thermocouple temperature sensor on a Raspberry Pi.

Designed specifically to work with the [Adafruit MAX31856 sensor](https://www.adafruit.com/products/3263).

Installing dependencies
-----------------------
Run the following:

````
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus
````

Installing Library
------------------

cd to your desired source directory and clone the repository:

````
git clone https://github.com/johnrbnsn/Adafruit_Python_MAX31856.git
````

Running Example/ Tests
----------------------

cd into the cloned repository and run the following command if you want the library installed (you can run tests without installing, but examples will not work):

````
sudo python setup.py install
````

Examples are in the examples directory, or tests are in the [Adafruit\_MAX31856] (https://github.com/johnrbnsn/Adafruit_Python_MAX31856/tree/master/Adafruit_MAX31856) directory.

Debugging
---------

If you are having issues, run the tests located in the [Adafruit\_MAX31856] (https://github.com/johnrbnsn/Adafruit_Python_MAX31856/tree/master/Adafruit_MAX31856) directory by:

````
python test_MAX31856.py -v
````

The resulting output and the test_MAX31856.log file should help with debugging the issue.

Supporting Developer
--------------------
Please consider supporting me if you found this code helpful: [paypal.me/johnrbnsn](http://paypal.me/johnrbnsn)

Acknowledgement
---------------
This code was modeled after the [Adafruit MAX31855 repository](https://github.com/adafruit/Adafruit_Python_MAX31855) which works with the prior version of this thermocouple amplifier.  There is only an Arduino example available from Adafruit at this time, since I use RasPi, I created this library.
