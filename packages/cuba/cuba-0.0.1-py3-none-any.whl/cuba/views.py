from cuba.routes import get_routes
from cuba.inspect import get_members, get_view_attributes, set_view_attributes
from cuba.decorators import handle_arguments_and_annotations

from cuba.types import ResponseType


class View(object): # this object is almost one-to-one copy of flask-classy view object

    ROUTE_PREFIX = None
    ROUTE_BASE = None
    TRAILING_SLASH = True

    SPECIAL_METHODS = [
        "get",
        "put",
        "post",
        "index",
        "delete",
    ]

    RESPONSE_TYPE = None

    def get_class_name(self) -> str:
        return self.__class__.__name__

    def get_route_base(self) -> str:
        class_name = self.get_class_name().lower()
        view_name, *rest = class_name.split("view")
        return "{0}".format(view_name)

    @property
    def routes(self) -> dict:
        for name, view in get_members(self):
            attributes = get_view_attributes(self, view)
            view = set_view_attributes(view, attributes)
            for (method, route) in get_routes(self, attributes):
                yield (method, route, handle_arguments_and_annotations(view))

    def register(self, app) -> None:
        for (method, route, handler) in self.routes:
            print(method, route, handler)
            app.router.add_route(method, route, handler)


class JSONView(View):

    RESPONSE_TYPE = ResponseType.JSON
