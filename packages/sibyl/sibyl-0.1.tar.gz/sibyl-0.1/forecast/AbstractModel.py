from common.vectorize import *

class AbstractModel:
  def __init__(self, params):
    self.params = params
    self.name = 'Abstract Model'
    self.sampe = None

  def modelName():
    return self.name

  def modelParameters(self):
      return self.params

  def describe(self):
    return 'model=%s, parameters=%s'  % (self.modelName(), self.modelParameters())

  def getSAMPE(self):
    """
    Symmetric mean absolute percentage error.
    """
    assert self.sampe != None , 'SAMPE hasn\'t been computed with a testing set'
    return self.sampe

  def computeSAMPE(self, actualValues, forecastValues):
    assert len(actualValues) == len(forecastValues), 'Length of actual values and forecast values must the same'

    absErrors = vectorAbs(vectorSubtract(actualValues, forecastValues))
    midValues = vectorMultiply(vectorAdd(actualValues, forecastValues), 0.5)
    midValueInverse = vectorInverse(midValues)

    self.sampe = vectorInnerProd(absErrors, midValueInverse) / len(actualValues)


  def trainAndTest(self, data, trainingRatio=0.8):
    """
    Since time serail model always requires processing train and test on a same data. Let's combine it together.
    """
    totalLength = len(data)
    traningLength = int(totalLength * trainingRatio)
    trainingData = data[:traningLength]
    testingData = data[traningLength:]

    self.train(trainingData)
    self.test(testingData)






