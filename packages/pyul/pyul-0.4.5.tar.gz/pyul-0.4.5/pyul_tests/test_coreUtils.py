import os

from pyul.support import unittest
from pyul.coreUtils import *

class TestCaseCommon(unittest.TestCase):
    
    def setUp(self):
        synthesize(self, 'mySynthesizeVar', None)
    
    def test_wildcard_to_re(self):
        self.assertEquals(wildcard_to_re('c:\CIG\main\*.*'),
                          '(?i)c\\:\\\\CIG\\\\main\\\\[^\\\\]*\\.[^\\\\]*$')
        self.assertEquals(wildcard_to_re('c:\CIG\main\*.*'),
                          wildcard_to_re('c:/CIG/main/*.*'))
    
    def test_synthesize(self):
        self.assertIn('_mySynthesizeVar', self.__dict__)
        self.assertTrue(hasattr(self, 'mySynthesizeVar'))        
        self.assertTrue(hasattr(self, 'getMySynthesizeVar'))
        self.assertTrue(hasattr(self, 'setMySynthesizeVar'))
        
        self.assertEqual(self.getMySynthesizeVar(), self.mySynthesizeVar)
        
    def test_get_class_name(self):
        self.assertEqual(get_class_name(self), 'TestCaseCommon')

class TestCaseDotifyDict(unittest.TestCase):
    
    def setUp(self):
        self.dotifydict = DotifyDict({'one':{'two':{'three':'value'}}})
        
    def test_dotifydict(self):
        self.assertEquals(self.dotifydict.one.two, {'three':'value'})
        self.dotifydict.one.two.update({'three':3,'four':4})
        self.assertEquals(self.dotifydict.one.two.four, 4)
        self.assertEquals(self.dotifydict.one, self.dotifydict.one)
        self.assertIn('two.three', (self.dotifydict.one))
        self.assertEquals(str(self.dotifydict), "{'one': {'two': {'four': 4, 'three': 3}}}")
        self.assertEquals(self.dotifydict.one.two, eval(str(self.dotifydict.one.two)))