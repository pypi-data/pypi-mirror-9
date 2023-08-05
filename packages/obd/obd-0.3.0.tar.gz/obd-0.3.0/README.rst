python-OBD
==========

A python module for handling realtime sensor data from OBD-II vehicle
ports. Works with ELM327 OBD-II adapters, and is fit for the Raspberry
Pi.

Installation
------------

.. code:: shell

    $ pip install obd

Basic Usage
-----------

.. code:: python

    import obd

    connection = obd.OBD() # auto-connects to USB or RF port

    cmd = obd.commands.RPM # select an OBD command (sensor)

    response = connection.query(cmd) # send the command, and parse the response

    print(response.value)
    print(response.unit)

Documentation
-------------

`Visit the GitHub Wiki!`_

Commands
--------

Here are a handful of the supported commands (sensors). For a full list,
see `the wiki`_

*note: support for these commands will vary from car to car*

-  Calculated Engine Load
-  Engine Coolant Temperature
-  Fuel Pressure
-  Intake Manifold Pressure
-  Engine RPM
-  Vehicle Speed
-  Timing Advance
-  Intake Air Temp
-  Air Flow Rate (MAF)
-  Throttle Position
-  Engine Run Time
-  Fuel Level Input
-  Number of warm-ups since codes cleared
-  Barometric Pressure
-  Ambient air temperature
-  Commanded throttle actuator
-  Time run with MIL on
-  Time since trouble codes cleared
-  Hybrid battery pack remaining life
-  Engine fuel rate

License
-------

GNU GPL v2

This library is forked from:

-  https://github.com/peterh/pyobd
-  https://github.com/Pbartek/pyobd-pi

Enjoy and drive safe!

.. _Visit the GitHub Wiki!: http://github.com/brendanwhitfield/python-OBD/wiki
.. _the wiki: https://github.com/brendanwhitfield/python-OBD/wiki/Command-Tables

