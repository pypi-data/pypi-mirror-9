'''
Created on 5 Dec 2013

@author: Akul Mathur
'''
import unittest

from flatten import flatten


class Test(unittest.TestCase):


    def setUp(self):
        self.l = [[1, 2, 3], [4, 5, 6], [7], [8, 9]]


    def tearDown(self):
        del self.l


    def testFlatten(self):
        self.assertIsInstance(flatten.flattenlist(self.l), list)
    
    def testMultiple_Recursive_List_Flatten(self):
        for i in [33, 66, 99, 132, 1320]:
            self.l *= i
            print flatten.flattenlist(self.l)
            self.assertIsInstance(flatten.flattenlist(self.l), list)
            self.l = [[1, 2, 3], [4, 5, 6], [7], [8, 9]]


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
