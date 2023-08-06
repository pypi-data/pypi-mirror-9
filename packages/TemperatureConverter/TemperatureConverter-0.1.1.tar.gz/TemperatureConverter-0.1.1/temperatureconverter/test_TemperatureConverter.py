# TemperatureConverter Tests

import unittest
from TemperatureConverter import TemperatureConverter
from TemperatureErrors import *

class KnownValues(unittest.TestCase):
  knownValues = (
    (0, 32),
    (100, 212)
  )

  temp_converter = TemperatureConverter()

  # test value conversions
  def testCtoF(self):
    """cToF should return the known Fahrenheit value for the
       provided Celsius value."""
    for c_val, f_val in self.knownValues:
      result = self.temp_converter.cToF(c_val)
      self.assertEqual(result, f_val)

  def testCtoK(self):
    """cToK should return 273.15 Kelvin for 0 Celsius"""
    result = self.temp_converter.cToK(0)
    self.assertEqual(result, 273.15)

  def testFtoC(self):
    """fToC should return the known Celsius value for the 
       provided Fahrenheit value."""
    for c_val, f_val in self.knownValues:
      result = self.temp_converter.fToC(f_val)
      self.assertEqual(result, c_val)

  def testFtoK(self):
    """fToK should return 273.15 Kelvin for 32 Fahrenheit"""
    result = self.temp_converter.fToK(32)
    self.assertEqual(result, 273.15)

  def testKtoC(self):
    """kToC should return 0 Celsius for 273.15 Kelvin"""
    result = self.temp_converter.kToC(273.15)
    self.assertEqual(result, 0)

  def testKtoF(self):
    """kToF should return 32 Fahrenheit for 273.15 Kelvin"""
    result = self.temp_converter.kToF(273.15)
    self.assertEqual(result, 32)

  # sanity checks
  def testCToKtoC(self):
    """Celsius to Kelvin to Celsius yields initial Celsius value"""
    original_celsius_value = 20
    kelvin_value = self.temp_converter.cToK(original_celsius_value)
    new_celsius_value = self.temp_converter.kToC(kelvin_value)
    self.assertEqual(original_celsius_value, new_celsius_value)

  def testCToFToC(self):
    """Celsius to Fahrenheit to Celsius yields initial Celsius value"""
    original_celsius_value = 20
    fahrenheit_value = self.temp_converter.cToF(original_celsius_value)
    new_celsius_value = self.temp_converter.fToC(fahrenheit_value)
    self.assertEqual(original_celsius_value, new_celsius_value)

  def testKToFToK(self):
    """Kelvin to Fahrenheit to Kelvin yields initial Kelvin value"""
    original_kelvin_value = 20
    fahrenheit_value = self.temp_converter.kToF(original_kelvin_value)
    new_kelvin_value = self.temp_converter.fToK(fahrenheit_value)
    self.assertEqual(original_kelvin_value, new_kelvin_value)

  # test range exceptions
  def testCtoFRange(self):
    """cToF should raise CelsiusRangeError if Celsius is less than -273.15"""
    self.assertRaises(CelsiusRangeError, self.temp_converter.cToF, -274)

  def testCtoKRange(self):
    """cToK should raise CelsiusRangeError if Celsius is less than -273.15"""
    self.assertRaises(CelsiusRangeError, self.temp_converter.cToK, -274)

  def testFtoCRange(self):
    """fToC should raise FahrenheitRangeError if Fahrenheit is less than -459.67"""
    self.assertRaises(FahrenheitRangeError, self.temp_converter.fToC, -460)

  def testFtoKRange(self):
    """fToK should raise FahrenheitRangeError if Fahrenheit is less than -459.67"""
    self.assertRaises(FahrenheitRangeError, self.temp_converter.fToK, -460)

  def testKtoCRange(self):
    """kToC should raise KelvinRangeError if Kelvin is less than 0"""
    self.assertRaises(KelvinRangeError, self.temp_converter.kToC, -1)

  def testKtoFRange(self):
    """kToF should raise KelvinRangeError if Kelvin is less than 0"""
    self.assertRaises(KelvinRangeError, self.temp_converter.kToF, -1)

if __name__ == '__main__':
  unittest.main()