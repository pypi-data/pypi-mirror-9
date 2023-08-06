from rivr.middleware import Middleware
from rivr_jinja.response import JinjaResponse


class JinjaMiddleware(Middleware):
    def __init__(self, environment, *args, **kwargs):
        super(JinjaMiddleware, self).__init__(*args, **kwargs)
        self.environment = environment

    def process_response(self, request, response):
        if isinstance(response, JinjaResponse):
            response.environment = self.environment

        return response
