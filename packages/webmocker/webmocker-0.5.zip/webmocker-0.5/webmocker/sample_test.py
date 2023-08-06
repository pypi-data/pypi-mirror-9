__author__ = 'admin'
import stubbing_engine
import unittest
import requests
import os
import time

class WebTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["stub_files_path"] = 'web_stubs/'
        stubbing_engine.start(port_number=8001)

    @classmethod
    def tearDownClass(cls):
        stubbing_engine.stop()

    def test_case1(self):
        capture = {}
        captured = requests.get('http://127.0.0.1:8001/with/query?search=Some text&searchtext=sheltonpaulinfant')
        print(captured.status_code)
        print(captured.text)
        self.assertEqual(captured.status_code, 230)

    def test_case2(self):
        capture = {}
        payload = "<status>OK</status>"
        captured = requests.post('http://127.0.0.1:8001/with/body', data=payload)
        print(captured.status_code)
        print(captured.text)
        self.assertEqual(captured.status_code, 270)
        self.assertEqual(captured.text, "This is a POST Request with matches clause")

    def test_case6(self):
        capture = {}
        payload = "123ERROORfsdfd"
        captured = requests.post('http://127.0.0.1:8001/with/body', data=payload)
        print(captured.status_code)
        print(captured.text)
        self.assertEqual(captured.status_code, 270)
        self.assertEqual(captured.text, "This is a POST Request with doesnt match clause")

    def test_case3(self):
        capture = {}
        captured = requests.get('http://127.0.0.1:8001/with/query/extra/path?search=Some text&searchtext=sheltonpaulinfant&firstName=paul&lastName=infant')
        print(captured.status_code)
        print(captured.text)
        self.assertEqual(captured.status_code, 230)
        self.assertEqual(captured.text, "This is a URL Path")

    def test_case4(self):
        capture = {}
        captured = requests.get('http://127.0.0.1:8001/some/thing')
        print(captured.headers)
        print(captured.text)
        self.assertEqual(captured.status_code, 210)
        # self.assertEqual(captured.text,"Hello world! This request has respnse headers")
        self.assertEqual(captured.headers["header1"],'respose Headers')
        self.assertEqual(captured.headers["content-type"],'text/json')
        print(captured.headers)

    def test_case5(self):
        capture = {}
        headers = {'content-type': 'text/xml','Accept' : 'text/jsondsadsa','ramp' : 'thissample','X-Custom-Header':'2134thisisthenight','etag':'123abbccd1234'}
        captured = requests.post('http://127.0.0.1:8001/with/headers',headers = headers)
        print(captured.status_code)
        print("Response Text : " +captured.text)
        self.assertEqual(captured.status_code, 250)
        self.assertEqual(captured.text, "This request URL has headers")

    def test_case7(self):
        capture = {}
        payload = "<status>OK</status>1323"
        captured = requests.post('http://127.0.0.1:8001/with/body', data=payload)
        print(captured.status_code)
        print(captured.text)
        self.assertEqual(captured.status_code, 270)
        self.assertEqual(captured.text, "This is a POST Request with match and doesnot match clause")

    def test_case8(self):
        capture = {}
        payload = "this is body"
        captured = requests.post('http://127.0.0.1:8001/body/with_nopattern', data=payload)
        print(captured.status_code)
        print(captured.text)
        self.assertEqual(captured.status_code, 200)
        self.assertEqual(captured.text, "This is body with no pattern")

    def test_case9(self):
        capture = {}
        captured = requests.get('http://127.0.0.1:8001/some/fromfile')
        print(captured.headers)
        print("Thisis the data from the file")
        # print(captured.text)
        self.assertEqual(captured.status_code, 210)
        # self.assertEqual(captured.text,"Hello world! This request has respnse headers")
        self.assertEqual(captured.headers["header1"],'respose Headers')
        self.assertEqual(captured.headers["content-type"],'text/json')
        print(captured.headers)

if __name__ == '__main__':
    unittest.main()
