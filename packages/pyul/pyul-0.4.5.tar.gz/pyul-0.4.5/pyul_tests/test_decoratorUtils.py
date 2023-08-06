
from pyul.support import unittest
from pyul.decoratorUtils import *

class TestCaseDecorators(unittest.TestCase):
    
    @Safe
    def test_safe(self):
        1/0
    
    @Timer
    def test_timer(self, timer):
        for i in range(5):
            time.sleep(2)
            timer.newLap(i)
            
    @Profile
    def test_profile(self):
        for i in range(5):
            (1 / 20 * 5 - 10 + 15) == 1