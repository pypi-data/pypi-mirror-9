class TemperatureError(Exception): pass

class TemperatureRangeError(TemperatureError):
  def __init__(self, temperature):
    self.value = "%s is below absolute 0 and therefore impossible." % temperature
  def __str__(self):
    return repr(self.value)

class CelsiusRangeError(TemperatureRangeError):
  def __init__(self, temperature):
    temperature = "%sC" % temperature
    super(CelsiusRangeError, self).__init__(temperature)

class FahrenheitRangeError(TemperatureRangeError):
  def __init__(self, temperature):
    temperature = "%sF" % temperature
    super(FahrenheitRangeError, self).__init__(temperature)

class KelvinRangeError(TemperatureRangeError):
  def __init__(self, temperature):
    temperature = "%sK" % temperature
    super(KelvinRangeError, self).__init__(temperature)