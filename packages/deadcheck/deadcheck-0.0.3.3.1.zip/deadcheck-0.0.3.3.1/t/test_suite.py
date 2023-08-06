'''
Created on Mar 10, 2015

Test Suite Created for the purpose of including a test suite inside the setup
file. This allows the user to run tests while setting up the module inside
python.

@author: harsnara

@change:  2015-03-10    First Draft.
'''
import unittest
from deadcheck.deadcheck import DeadcheckAPI

class TestDeadCheckAPIFailure(unittest.TestCase):
    def setUp(self):
        self.checker = DeadcheckAPI()
        
    def runTest(self):
        print "\nRunning Check For Failure Case\n"
        self.urlObj = self.checker.amIDead('https://pypi.python.org/pypiy')
        self.dead   = self.urlObj.isBroken()
        print self.urlObj.info()
        self.failUnless(self.dead, 'Invalid URL Test Failed.')
    
    def tearDown(self):
        print "\nCleaning up Failure Test Case\n"
        
class TestDeadCheckAPIPass(unittest.TestCase):
    def setUp(self):
        self.checker = DeadcheckAPI()
        
    def runTest(self):
        print "\nRunning Check for Pass Case\n"
        self.urlObj = self.checker.amIDead('https://pypi.python.org/pypi')
        self.dead   = self.urlObj.isBroken()
        print self.urlObj.info()
        self.failIf(self.dead, 'Valid URL Test Failed.')
    
    def tearDown(self):
        print "\nCleaning Up pass Test Case\n"

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestDeadCheckAPIFailure())
    suite.addTest(TestDeadCheckAPIPass())
    return suite

if __name__ == '__main__' :
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)()