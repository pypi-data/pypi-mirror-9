from unittest import TestCase

from cuba import routes
from cuba.tests.base import SampleView
from cuba.inspect import get_view_attributes


class TestRoutesUtils(TestCase):

    def setUp(self):
        self.view = SampleView()

    def test_get_route_arguments(self):
        attributes = get_view_attributes(self.view, self.view.index)
        arguments = routes.get_route_arguments(attributes)
        self.assertEqual(arguments, None)

        attributes = get_view_attributes(self.view, self.view.get_collection_item)
        arguments = routes.get_route_arguments(attributes)
        self.assertEqual(arguments, "{collection}/{item}")

    def test_get_route_argument_name(self):
        arguments = routes.get_route_argument_name(["collection", "item"])
        self.assertEqual(list(arguments), ["{collection}", "{item}"])

    def test_get_routes(self):
        attributes = get_view_attributes(self.view, self.view.index)
        routes_ = routes.get_routes(self.view, attributes)
        self.assertEqual(list(routes_), [
            ('GET', '/sample/')
        ])

        attributes = get_view_attributes(self.view, self.view.get)
        routes_ = routes.get_routes(self.view, attributes)
        self.assertEqual(list(routes_), [
            ('GET', '/sample/{uid}/')
        ])

        attributes = get_view_attributes(self.view, self.view.get_collection_item)
        routes_ = routes.get_routes(self.view, attributes)
        self.assertEqual(list(routes_), [
            ("GET", "/sample/get_collection_item/{collection}/{item}/"),
            ("POST", "/sample/get_collection_item/{collection}/{item}/"),
            ("PUT", "/sample/get_collection_item/{collection}/{item}/"),
            ("DELETE", "/sample/get_collection_item/{collection}/{item}/")
        ])

    def test_get_route(self):
        attributes = get_view_attributes(self.view, self.view.get_collection_item)
        route = routes.get_route(self.view, attributes)
        self.assertEqual(route, "/sample/get_collection_item/{collection}/{item}/")

        self.view.TRAILING_SLASH = False
        attributes = get_view_attributes(self.view, self.view.get_collection_item)
        route = routes.get_route(self.view, attributes)
        self.assertEqual(route, "/sample/get_collection_item/{collection}/{item}")

        self.view.ROUTE_BASE = "/actions"
        attributes = get_view_attributes(self.view, self.view.get_collection_item)
        route = routes.get_route(self.view, attributes)
        self.assertEqual(route, "/actions/get_collection_item/{collection}/{item}")

        self.view.ROUTE_BASE = "/"
        attributes = get_view_attributes(self.view, self.view.get_collection_item)
        route = routes.get_route(self.view, attributes)
        self.assertEqual(route, "/get_collection_item/{collection}/{item}")

        attributes = get_view_attributes(self.view, self.view.index)
        route = routes.get_route(self.view, attributes)
        self.assertEqual(route, "/")

        self.view.ROUTE_PREFIX = "/api"
        attributes = get_view_attributes(self.view, self.view.get_collection_item)
        route = routes.get_route(self.view, attributes)
        self.assertEqual(route, "/api/get_collection_item/{collection}/{item}")
