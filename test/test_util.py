import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from util import save_json_file 
from hashlib import md5
from mmh3 import hash128
from xxhash import xxh128_hexdigest
import json

class TestUtil(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.JSON_FILENAME = 'test.json'
    
    def tearDown(self):
        os.system(f'rm {self.JSON_FILENAME}')

    def test_save_json_file(self):
        self.assertFalse(os.path.exists(self.JSON_FILENAME))
        data = {'f1': md5("def f1():\n\treturn 'f1'".encode('utf')).hexdigest(),
                'f2': hash128("def f2(a, b, c=3):\n\treturn a ** b + c".encode('utf')),
                'f3': xxh128_hexdigest("def f3(x, y):\n\treturn x/y".encode('utf'))}
        save_json_file(data, self.JSON_FILENAME)
        self.assertTrue(os.path.exists(self.JSON_FILENAME))
        with open(self.JSON_FILENAME) as f:
            data2 = json.load(f)
        self.assertDictEqual(data, data2)

if __name__ == '__main__':
    unittest.main()