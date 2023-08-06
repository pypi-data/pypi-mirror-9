from common.vectorize import *
from AbstractModel import AbstractModel

PARAM_PERIOD = 'period'

class SeasonalityByAverageModel(AbstractModel):
  """
  Simple Seasonality model.
  The value on x is the average of its previous period.
  F(x) = Average(x - period * t) t = [1, )
  """
  def __init__(self, params):
    self.params = params
    self.name = 'Seasonality model by simple average'
    self.checkParams()
    self.period = params[PARAM_PERIOD]
    self.averageSeaon = []
    self.sampe = None

  def checkParams(self):
    assert PARAM_PERIOD in self.params, 'Need a period param'

  def train(self, data):
    self.data = data[:]
    period = self.period
    length = len(self.data)
    repeatCount = len(self.data) / period

    self.averageSeaon = [0] * period
    for i in xrange(repeatCount):
      self.averageSeaon = vectorAdd(self.averageSeaon,
          self.data[(length - (i + 1) * period) : (length - i * period)])
    self.averageSeaon = vectorMultiply(self.averageSeaon, 1.0 / repeatCount)

  def forecast(self, nAhead):
    """
    Forecast nAhead future values.
    """
    assert len(self.averageSeaon) > 0, 'This model hasn\'t been trained'
    forecastValues = self.averageSeaon * (int(nAhead / self.period) + 1)
    forecastValues = forecastValues[:nAhead]
    return forecastValues

  def test(self, data):
    length = len(data)
    forecastValues = self.forecast(length)
    self.computeSAMPE(data, forecastValues)



















