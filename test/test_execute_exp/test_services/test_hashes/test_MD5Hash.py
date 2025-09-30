import unittest, os, sys, hashlib
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.hashes.MD5Hash import MD5Hash


class TestMD5Hash(unittest.TestCase):
    def setUp(self):
        self.first_output = os.urandom(16)
        self.second_output = os.urandom(16)
        self.serializer = Mock()
        self.serializer.dumps = Mock(side_effect=[self.first_output, self.second_output])

        self.hash = MD5Hash(self.serializer)

    def test_get_id_with_source_args_and_kwargs(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'
        result = self.hash.get_id(source, fun_args=[-1.227, 0], fun_kwargs={'z': -12.5})

        data = (str(self.first_output + self.second_output) + source).encode('utf')
        expected_result = hashlib.md5(data).hexdigest()

        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
