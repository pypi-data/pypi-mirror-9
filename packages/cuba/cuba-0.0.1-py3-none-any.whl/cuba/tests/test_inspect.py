from unittest import TestCase
from cuba.tests.base import SampleView

from cuba import inspect
from cuba.types import ResponseType


class UtilsTestCase(TestCase):

    def setUp(self):
        self.view = SampleView()

    def test_get_members(self):
        members = inspect.get_members(self.view)
        self.assertEqual(sorted(m[0] for m in members), [
            "get",
            "get_collection_item",
            "index",
            "returns",
            "sample"
        ])

    def test_get_view_name(self):
        name = inspect.get_view_name(self.view.sample)
        self.assertEqual(name, "sample")

        name = inspect.get_view_name(self.view.returns)
        self.assertEqual(name, "returns")

    def test_get_view_arguments(self):
        arguments = inspect.get_view_arguments(self.view.sample)
        self.assertEqual(arguments, ["uid"])

        arguments = inspect.get_view_arguments(self.view.returns)
        self.assertEqual(arguments, [])

    def test_get_view_annotations(self):
        annotations = inspect.get_view_annotations(self.view.sample)
        self.assertEqual(annotations, {"uid": int})

        annotations = inspect.get_view_annotations(self.view.returns)
        self.assertIn("return", annotations)

    def test_get_view_attributes(self):
        attributes = inspect.get_view_attributes(self.view, self.view.sample)
        self.assertEqual(attributes.get("name"), "sample")
        self.assertEqual(attributes.get("methods"), ["GET"])
        self.assertEqual(attributes.get("arguments"), ["uid"])
        self.assertEqual(attributes.get("annotations"), {"uid": int})
        self.assertEqual(attributes.get("returns"), None)

        attributes = inspect.get_view_attributes(self.view, self.view.returns)
        self.assertEqual(attributes.get("name"), "returns")
        self.assertEqual(attributes.get("methods"), ["GET"])
        self.assertEqual(attributes.get("arguments"), [])
        self.assertEqual(attributes.get("annotations"), {})
        self.assertEqual(attributes.get("returns"), ResponseType.JSON)
