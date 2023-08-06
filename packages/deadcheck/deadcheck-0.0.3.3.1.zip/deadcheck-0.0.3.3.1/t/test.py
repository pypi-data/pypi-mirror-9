'''
Created on Jul 28, 2014

@author: harsnara
'''
import unittest
from deadcheck.deadcheck import DeadcheckAPI

class TestDeadCheckAPI(unittest.TestCase):


    def setUp(self):
        ## Modify this to Include Proxy information if you are running the script under a protected network. 
        self.checker = DeadcheckAPI()
        
    def runCheck(self, url):
        self.urlObj = self.checker.amIDead(url)
        self.dead = self.urlObj.isBroken()
        
        if self.dead:
            self.testVal = 0
        else:
            self.testVal = 1

    def testValid(self):
        self.runCheck('https://pypi.python.org/pypi')
        self.assertEqual(self.testVal, 1, 'Test 1 For Valid Link Test Failed')
        print self.urlObj.info()
        
    def testInvalid(self):
        self.runCheck('https://pypi.python.org/pypiy')
        self.assertEqual(self.testVal, 0, 'Invalid Url Test Failed.')
        print self.urlObj.info()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()