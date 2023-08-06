__author__ = 'luofan'
import sys
import os
sys.path.append(os.path.dirname(__file__) + "/../")
import unittest
import time
from bae.cli.Auth_tools import authTool

class authToolTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testStringKey(self):
        time_str = "2014-12-31 10:00:00"
        time_stamp = int(time.mktime(time.strptime(time_str,"%Y-%m-%d %H:%M:%S")))
        ret = authTool.stringkey(ak = "123", sk= "123" , time_stamp=time_stamp,expiration= 10)
        self.assertEquals(ret,"123")


unittest.main()

