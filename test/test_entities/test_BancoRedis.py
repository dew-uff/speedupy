import os, sys, unittest
from unittest.mock import Mock, patch, call

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from entities.BancoRedis import BancoRedis


class TestSetGroupOfKeyValuePairs(unittest.TestCase):
    @patch('entities.BancoRedis.redis.Redis')
    def test_set_group_of_key_value_pairs_when_data_requires_multiple_pipelines_to_be_saved(self, mock_redis):
        value_512mb = b"x" * int(512 * 1024 * 1024)
        data = {"k1": value_512mb,
                "k2": value_512mb,
                "k3": value_512mb}

        pipeline1 = Mock()
        pipeline2 = Mock()

        banco = BancoRedis()
        banco.client.pipeline.side_effect = [pipeline1, pipeline2]


        banco.set_group_of_key_value_pairs(data)


        self.assertEqual(banco.client.pipeline.call_count, 2)

        self.assertEqual(pipeline1.set.call_count, 2)
        pipeline1.set.assert_any_call("k1", value_512mb)
        pipeline1.set.assert_any_call("k2", value_512mb)
        pipeline1.execute.assert_called_once()

        pipeline2.set.assert_called_once_with("k3", value_512mb)
        pipeline2.execute.assert_called_once()
