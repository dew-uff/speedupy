import unittest, os, sys
from unittest.mock import Mock, call

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.hashes.Hash import Hash


class TestHash(unittest.TestCase):
    def setUp(self):
        self.first_dumps_output = os.urandom(16)
        self.second_dumps_output = os.urandom(16)
        self.serializer = Mock()
        self.serializer.dumps = Mock(side_effect=[self.first_dumps_output, self.second_dumps_output])
        self.serializer.clean_data = Mock(side_effect=lambda x: x)

        self.hash = Hash(self.serializer)

        self.hash._hash = Mock()

    def test_get_id_without_fun_args(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'

        self.hash.get_id(source, fun_kwargs={'z': -12.5})

        self.serializer.clean_data.assert_called_once_with({'z': -12.5})
        self.serializer.dumps.assert_called_once_with({'z': -12.5})
        expected_args = (str(self.first_dumps_output) + source).encode('utf')
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_without_fun_kwargs(self):
        source = 'print("Testando!")\nos.path.exists("/")\nrandom.randint()\nreturn x + y / -z'

        self.hash.get_id(source, fun_args=[-1.227, 0])

        self.serializer.clean_data.assert_called_once_with([-1.227, 0])
        self.serializer.dumps.assert_called_once_with([-1.227, 0])
        expected_args = (str(self.first_dumps_output) + source).encode('utf')
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_only_with_fun_source(self):
        source = 'print("Testando!")\nreturn x / y ** 2'

        self.hash.get_id(source)

        self.serializer.clean_data.assert_not_called()
        self.serializer.dumps.assert_not_called()
        expected_args = ("b''" + source).encode('utf')
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_with_source_args_and_kwargs(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'

        self.hash.get_id(source, fun_args=[-1.227, 0], fun_kwargs={'z': -12.5})

        self.assertEqual(self.serializer.clean_data.call_count, 2)
        self.serializer.clean_data.assert_has_calls([call([-1.227, 0]), call({'z': -12.5})])
        self.assertEqual(self.serializer.dumps.call_count, 2)
        self.serializer.dumps.assert_has_calls([call([-1.227, 0]), call({'z': -12.5})])
        expected_args = (str(self.first_dumps_output + self.second_dumps_output) + source).encode('utf')
        self.hash._hash.assert_called_once_with(expected_args)

if __name__ == '__main__':
    unittest.main()
