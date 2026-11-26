import os
import random
from typing import Dict

from remove_paths import remove_paths

from constants import Constants
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.CloudpickleSerializer import CloudpickleSerializer
from execute_exp.services.serializers.PickleSerializer import PickleSerializer
from execute_exp.services.storages.Storage import Storage


class AbstractStorageTest(object):
    def setUp(self):
        self.drop_env()
        self.create_env()
        self.serializer = random.choice([PickleSerializer(), CloudpickleSerializer()])
        self.storage = self.create_instance(self.serializer)
        self.assert_storage_is_empty()

    def tearDown(self):
        self.drop_env()

    def drop_env(self):
        remove_paths(Constants().FOLDER_NAME)

    def create_env(self):
        os.makedirs(Constants().FOLDER_NAME)

    def create_instance(self) -> Storage:
        pass

    def assert_storage_is_empty(self):
        pass

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        pass

    def manually_cache_a_record(
        self, func_hash: str, func_return, func_name=None, **kwargs
    ):
        pass

    def assert_data_gotten_is_correct(
        self, data_gotten: Dict[str, CacheData], expected_data: Dict[str, CacheData]
    ):
        self.assertEqual(len(data_gotten), len(expected_data))
        self.assertSetEqual(set(data_gotten.keys()), set(expected_data.keys()))
        for func_call_hash in data_gotten:
            self.assert_two_cache_data_are_equal(
                data_gotten[func_call_hash], expected_data[func_call_hash]
            )

    def assert_two_cache_data_are_equal(
        self, cache_data_1: CacheData, cache_data_2: CacheData
    ):
        self.assertEqual(
            cache_data_1.function_call_hash, cache_data_2.function_call_hash
        )
        self.assertEqual(cache_data_1.func_name, cache_data_2.func_name)
        self.assertEqual(
            self.serializer.dumps(cache_data_1.output),
            self.serializer.dumps(cache_data_2.output),
        )

    def test_get_all_cached_data_when_there_is_no_cache_record(self):
        cached_data = self.storage.get_all_cached_data()
        self.assertDictEqual(cached_data, {})

    def test_get_all_cached_data_when_there_is_one_cache_record(self):
        self.manually_cache_a_record("func_call_hash", (1, True, MyClass()))

        cached_data = self.storage.get_all_cached_data()

        expected_data = {
            "func_call_hash": CacheData("func_call_hash", (1, True, MyClass()))
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_all_cached_data_when_there_are_many_cache_records(self):
        self.manually_cache_a_record("func_call_hash1", (True, 2, 5))
        self.manually_cache_a_record("func_call_hash2", [{"key1": 10, "key_2": False}])
        self.manually_cache_a_record("func_call_hash3", -123.213)
        self.manually_cache_a_record("func_call_hash4", [1, 2.213, "test"])

        cached_data = self.storage.get_all_cached_data()

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", (True, 2, 5)),
            "func_call_hash2": CacheData(
                "func_call_hash2", [{"key1": 10, "key_2": False}]
            ),
            "func_call_hash3": CacheData("func_call_hash3", -123.213),
            "func_call_hash4": CacheData("func_call_hash4", [1, 2.213, "test"]),
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_all_cached_data_using_an_isolated_connection(self):
        self.manually_cache_a_record("func_call_hash1", -123.3, commit=True)
        self.manually_cache_a_record("func_call_hash2", True, commit=True)

        cached_data = self.storage.get_all_cached_data(use_isolated_connection=True)

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", -123.3),
            "func_call_hash2": CacheData("func_call_hash2", True),
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_cached_data_of_a_function_when_there_is_no_record(self):
        cached_data = self.storage.get_cached_data_of_a_function("f1")
        self.assertDictEqual(cached_data, {})

    def test_get_cached_data_of_a_function_when_there_is_cached_records_only_for_other_functions(
        self,
    ):
        self.manually_cache_a_record("func_call_hash1", (True, 2, 5), func_name="f2")
        self.manually_cache_a_record(
            "func_call_hash2", [{"key1": 10, "key_2": False}], func_name="f2"
        )
        self.manually_cache_a_record("func_call_hash3", -123.213, func_name="f3")

        cached_data = self.storage.get_cached_data_of_a_function("f1")
        self.assertDictEqual(cached_data, {})

    def test_get_cached_data_of_a_function_when_there_is_a_cached_record_for_it_and_for_other_functions_too(
        self,
    ):
        self.manually_cache_a_record("func_call_hash1", 5000.00, func_name="f1")
        self.manually_cache_a_record("func_call_hash11", (True, 2, 5), func_name="f1")
        self.manually_cache_a_record(
            "func_call_hash2", [{"key1": 10, "key_2": False}], func_name="f2"
        )
        self.manually_cache_a_record("func_call_hash3", -123.213, func_name="f3")

        cached_data = self.storage.get_cached_data_of_a_function("f1")

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", 5000.00, func_name="f1"),
            "func_call_hash11": CacheData(
                "func_call_hash11", (True, 2, 5), func_name="f1"
            ),
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_cached_data_of_a_function_when_there_are_many_cached_data_records_for_it(
        self,
    ):
        self.manually_cache_a_record("func_call_hash1", "testing", func_name="f1")
        self.manually_cache_a_record("func_call_hash2", (1,), func_name="f1")
        self.manually_cache_a_record("func_call_hash3", [10, -4, False], func_name="f1")
        self.manually_cache_a_record("func_call_hash4", -123.213, func_name="f3")

        cached_data = self.storage.get_cached_data_of_a_function("f1")

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", "testing", func_name="f1"),
            "func_call_hash2": CacheData("func_call_hash2", (1,), func_name="f1"),
            "func_call_hash3": CacheData(
                "func_call_hash3", [10, -4, False], func_name="f1"
            ),
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_cached_data_of_a_function_using_an_isolated_connection(self):
        self.manually_cache_a_record(
            "func_call_hash1", "My Test", func_name="f1", commit=True
        )
        self.manually_cache_a_record(
            "func_call_hash2", {1, 4, -2}, func_name="f1", commit=True
        )
        self.manually_cache_a_record("func_call_hash3", 10, func_name="f2", commit=True)
        self.manually_cache_a_record(
            "func_call_hash4", {1, 5, 4}, func_name="f2", commit=True
        )

        cached_data = self.storage.get_cached_data_of_a_function(
            "f1", use_isolated_connection=True
        )

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", "My Test", func_name="f1"),
            "func_call_hash2": CacheData("func_call_hash2", {1, 4, -2}, func_name="f1"),
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_cached_data_of_a_function_call_when_cache_record_doesnt_exist(self):
        cache_data = self.storage.get_cached_data_of_a_function_call("func_call_hash")
        self.assertIsNone(cache_data)

    def test_get_cached_data_of_a_function_call_when_cache_record_doesnt_exist_but_other_records_exist(
        self,
    ):
        self.manually_cache_a_record("func_call_hash1", "My Test")
        self.manually_cache_a_record("func_call_hash2", {1, 4, -2})
        self.manually_cache_a_record("func_call_hash3", 10)

        cache_data = self.storage.get_cached_data_of_a_function_call("func_call_hash0")
        self.assertIsNone(cache_data)

    def test_get_cached_data_of_a_function_call_when_cache_record_exists(self):
        self.manually_cache_a_record("func_call_hash1", 3.1415)
        self.manually_cache_a_record("func_call_hash2", [1, {2, 4, 1}, -2])
        self.manually_cache_a_record("func_call_hash3", "My test")

        cache_data = self.storage.get_cached_data_of_a_function_call("func_call_hash1")
        self.assert_two_cache_data_are_equal(
            cache_data, CacheData("func_call_hash1", 3.1415)
        )

    def test_get_cached_data_of_a_function_call_when_this_record_doesnt_exist_and_records_are_grouped_by_function_name(
        self,
    ):
        cache_data = self.storage.get_cached_data_of_a_function_call(
            "func_call_hash", func_name="f1"
        )
        self.assertIsNone(cache_data)

    def test_get_cached_data_of_a_function_call_when_this_record_exists_and_records_are_grouped_by_function_name(
        self,
    ):
        self.manually_cache_a_record("func_call_hash", "my_string", func_name="f1")

        cache_data = self.storage.get_cached_data_of_a_function_call(
            "func_call_hash", func_name="f1"
        )
        self.assert_two_cache_data_are_equal(
            cache_data, CacheData("func_call_hash", "my_string", func_name="f1")
        )

    def test_get_cached_data_of_a_function_call_using_an_isolated_connection(self):
        self.manually_cache_a_record("func_call_hash1", -3.1415, commit=True)
        self.manually_cache_a_record("func_call_hash2", [1, {2, 4, 1}, -2], commit=True)
        self.manually_cache_a_record("func_call_hash3", "My test", commit=True)

        cache_data = self.storage.get_cached_data_of_a_function_call(
            "func_call_hash1", use_isolated_connection=True
        )
        self.assert_two_cache_data_are_equal(
            cache_data, CacheData("func_call_hash1", -3.1415)
        )

    def test_save_cache_data_when_there_is_no_data_to_save(self):
        self.storage.save_cache_data({})
        self.assert_cached_data({})

    def test_save_cache_data_when_there_is_one_record_to_save_without_func_name(self):
        data = {"func_call_hash": CacheData("func_call_hash", {1, 5, 4})}
        self.storage.save_cache_data(data)
        self.assert_cached_data(data)

    def test_save_cache_data_when_there_is_one_record_to_save_with_func_name(self):
        data = {
            "func_call_hash": CacheData("func_call_hash", {1, True}, func_name="f1")
        }
        self.storage.save_cache_data(data)
        self.assert_cached_data(data)

    def test_save_cache_data_when_there_are_many_records_to_save_without_func_name(
        self,
    ):
        data = {
            "func_call_hash1": CacheData("func_call_hash1", {1, True}),
            "func_call_hash2": CacheData("func_call_hash2", ("test",)),
            "func_call_hash3": CacheData("func_call_hash3", -23.123),
        }
        self.storage.save_cache_data(data)
        self.assert_cached_data(data)

    def test_save_cache_data_when_there_are_many_records_to_save_with_func_name(self):
        data = {
            "func_call_hash1": CacheData("func_call_hash1", {1, True}, func_name="f1"),
            "func_call_hash2": CacheData("func_call_hash2", ("test",), func_name="f2"),
            "func_call_hash3": CacheData("func_call_hash3", -23.123, func_name="f2"),
            "func_call_hash4": CacheData("func_call_hash4", MyClass(), func_name="f3"),
        }
        self.storage.save_cache_data(data)
        self.assert_cached_data(data)

    def test_save_cache_data_with_func_name_when_there_are_already_other_entries_for_this_func_name(
        self,
    ):
        self.manually_cache_a_record("func_call_hash1", MyClass(), func_name="f1")

        data = {
            "func_call_hash2": CacheData("func_call_hash2", {1, True}, func_name="f1"),
            "func_call_hash3": CacheData("func_call_hash3", ("test",), func_name="f1"),
        }
        self.storage.save_cache_data(data)

        data.update(
            {"func_call_hash1": CacheData("func_call_hash1", MyClass(), func_name="f1")}
        )
        self.assert_cached_data(data)

    def test_save_cache_data_of_a_function_call_when_function_call_record_already_exists(
        self,
    ):
        self.manually_cache_a_record("func_call_hash", (True, 2, 5))

        data = {"func_call_hash": CacheData("func_call_hash", (True, 2, 5))}
        self.storage.save_cache_data(data)
        self.assert_cached_data(data)

    def test_save_cache_data_using_an_isolated_connection(self):
        data = {
            "func_call_hash1": CacheData("func_call_hash1", {1, True}, func_name="f1"),
            "func_call_hash2": CacheData("func_call_hash2", -23.123, func_name="f2"),
            "func_call_hash3": CacheData("func_call_hash3", MyClass(), func_name="f3"),
        }
        self.storage.save_cache_data(data, use_isolated_connection=True)
        self.assert_cached_data(data)


class MyClass:
    def __init__(self):
        self.__x = 10
        self.__y = 20
