import unittest, os, sys
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from setup_exp.services.PubSub import PubSub


class TestPubSub(unittest.TestCase):
    def setUp(self):
        self.pubsub = PubSub()
        self.calls = []

        self.cb1 = Mock()
        self.cb2 = Mock()
        self.cb3 = Mock()

    def test_subscribe_two_items_in_the_same_event(self):
        self.assertDictEqual(self.pubsub.subscribers, {})

        self.pubsub.subscribe("event", self.cb1)
        self.pubsub.subscribe("event", self.cb2)

        self.assertDictEqual(self.pubsub.subscribers, {"event": [self.cb1, self.cb2]})

    def test_subscribe_the_same_item_in_two_events(self):
        self.assertDictEqual(self.pubsub.subscribers, {})

        self.pubsub.subscribe("event1", self.cb1)
        self.pubsub.subscribe("event2", self.cb1)

        self.assertDictEqual(
            self.pubsub.subscribers, {"event1": [self.cb1], "event2": [self.cb1]}
        )

    def test_unsubscribe_item_that_is_not_subscribed(self):
        self.assertDictEqual(self.pubsub.subscribers, {})

        self.pubsub.unsubscribe("event", self.cb1)

        self.assertDictEqual(self.pubsub.subscribers, {"event": []})

    def test_unsubscribe_item_that_is_subscribed(self):
        self.pubsub.subscribe("event", self.cb1)
        self.pubsub.unsubscribe("event", self.cb1)
        self.assertDictEqual(self.pubsub.subscribers, {"event": []})

    def test_publish_event(self):
        self.pubsub.subscribe("event1", self.cb1)
        self.pubsub.subscribe("event1", self.cb2)
        self.pubsub.subscribe("event2", self.cb3)
        self.pubsub.publish("event1", "data")

        self.cb1.assert_called_once_with("data")
        self.cb2.assert_called_once_with("data")
        self.cb3.assert_not_called()


if __name__ == "__main__":
    unittest.main()
