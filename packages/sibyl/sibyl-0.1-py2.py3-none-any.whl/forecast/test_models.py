import sys
sys.path.append('./')

import unittest
import io
import json
from SeasonalityByAverageModel import SeasonalityByAverageModel

DATA_SET_FILE = './data/seasonalityTs.json'

class TestSeasonalityByAverageModel(unittest.TestCase):
  def setUp(self):
    self.model = SeasonalityByAverageModel({'period': 7})
    self.dataSet = json.loads(io.open(DATA_SET_FILE, 'r', encoding='utf-8').read())


  def testModelAccuracy(self):
    for key in self.dataSet:
      ts = self.dataSet[key]
      data = ts['data']
      self.model.trainAndTest(data)
      print 'SAMPE:%f' % self.model.getSAMPE()
      self.assertTrue(self.model.getSAMPE() < 0.2)

if __name__ == '__main__':
  unittest.main()



