from cuba import View, route
from cuba.types import ResponseType


class SampleView(View):

    def index(self, request):
        pass

    def get(self, request, uid: int):
        pass

    def sample(self, request, uid: int):
        pass

    def returns(self, request) -> ResponseType.JSON:
        pass

    @route(methods=["GET", "POST", "PUT", "DELETE"])
    def get_collection_item(self, request, collection: int, item: int) -> ResponseType.JSON:
        pass
