__author__ = 'admin'
import unittest
import requests
import sys
sys.path.append("E:\\repo\\pretend_extended\\pretend_extended\\client")
import http
import os

class WebTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        mock = http.HTTPMock('localhost', 8001,name='shel')
        mock.when('GET /thing*').reply('Hello',status=202,times=20)
    @classmethod

    def test_case1(self):
        capture = {}
        captured = requests.get('http://127.0.0.1:8001/mockhttp/shel/thingdsadsa')
        print(captured.status_code)
        print(captured.text)

        # captured = requests.get('http://localhost:8998/address/12')
        # print(captured.status_code)
        # status_code(captured.text)

if __name__ == '__main__':
    unittest.main()
