import unittest, os, sys, json
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
        self.serializer.to_canonical = Mock(side_effect=lambda x: x)

        self.hash = Hash(self.serializer)

        self.hash._hash = Mock()

    def test_get_id_without_fun_args(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'

        self.hash.get_id(source, fun_kwargs={'z': -12.5})

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.assertEqual(self.serializer.to_canonical.call_args_list, [call(()), call({'z': -12.5})])
        expected_args = json.dumps({"args": [],"kwargs": {'z': -12.5},"source": source},
                                    sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_without_fun_kwargs(self):
        source = 'print("Testando!")\nos.path.exists("/")\nrandom.randint()\nreturn x + y / -z'

        self.hash.get_id(source, fun_args=[-1.227, 0])

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.assertEqual(self.serializer.to_canonical.call_args_list, [call([-1.227, 0]), call({})])
        expected_args = json.dumps({"args": [-1.227, 0],"kwargs": {},"source": source},
                                    sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_only_with_fun_source(self):
        source = 'print("Testando!")\nreturn x / y ** 2'

        self.hash.get_id(source)

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.assertEqual(self.serializer.to_canonical.call_args_list, [call(()), call({})])
        expected_args =  json.dumps({"args": [],"kwargs": {},"source": source},
                                    sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_with_source_args_and_kwargs(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'

        self.hash.get_id(source, fun_args=[-1.227, 0], fun_kwargs={'z': -12.5})

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.serializer.to_canonical.assert_has_calls([call([-1.227, 0]), call({'z': -12.5})])
        expected_args = json.dumps({"args": [-1.227, 0],"kwargs": {'z': -12.5},"source": source},
                                    sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

if __name__ == '__main__':
    unittest.main()
