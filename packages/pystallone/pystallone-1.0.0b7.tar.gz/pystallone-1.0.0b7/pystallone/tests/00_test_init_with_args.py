import unittest2
import os


class TestInitWithArgs(unittest2.TestCase):
    
    def setUp(self):
        unittest2.TestCase.setUp(self)
        self.cp = os.environ.get('stallone_cp', '')
    
    def testWithArgsExtendClassPath(self):
        import pystallone
        args = ['-Xms64m']
        if self.cp:
            args.append('-Djava.class.path=%s' % self.cp)
    
        pystallone.startJVM(None, args)
        
        a = pystallone.API.doublesNew.array(10)
        
        self.assertEqual(10, a.size())
        