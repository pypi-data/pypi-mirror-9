=====================
Temperature Converter
=====================

Temperature Converter provides a basic class for converting
between Fahrenheit (F), Celsius (C), and Kelvin (K) temperatures.

Typical use might look like::

    #!/usr/bin/env python
    
    from temperatureconverter.TemperatureConverter import TemperatureConverter

    temp_converter = TemperatureConverter()
    print temp_converter.cToF(100)
    >> 212.0

Exceptions are raised if temperatures below absolute zero
(0 K) are provided.
