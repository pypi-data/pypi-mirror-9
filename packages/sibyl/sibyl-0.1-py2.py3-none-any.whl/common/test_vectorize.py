import random
import unittest
from vectorize import *


class TestVectorize(unittest.TestCase):
  def setUp(self):
    pass

  def testVectorize(self):
    self.assertEqual([2,4,6], vectorAdd([1,2,3], [1,2,3]))
    self.assertEqual([0,0,0], vectorSubtract([1,2,3], [1,2,3]))

    self.assertEqual([2,4,6], vectorMultiply([1,2,3], 2))
    self.assertEqual([2,8,18], vectorMultiply([1,2,3], [2,4,6]))

    self.assertEqual(14, vectorInnerProd([1,2,3], [1,2,3]))

    self.assertEqual([1,2,3], vectorAbs([-1,-2,-3]))

    self.assertEqual([1,2,3], vectorDivide([1,4,9], [1,2,3]))

    self.assertEqual([1.0/2,1.0/3,1.0/4], vectorInverse([2,3,4]))

  def testVectorizeFail(self):
    self.assertRaises(Exception, vectorAdd, ([1,2], [1,2,3]))

if __name__ == '__main__':
  unittest.main()
