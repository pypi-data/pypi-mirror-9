import unittest
from jinja2 import Environment

from rivr_jinja.response import JinjaResponse
from rivr_jinja.middleware import JinjaMiddleware


class JinjaMiddlewareTests(unittest.TestCase):
    def test_middleware_adds_environment_to_resoibse(self):
        environment = Environment()
        middleware = JinjaMiddleware(environment)

        response = JinjaResponse(None, None, {})
        middleware.process_response(None, response)

        self.assertEqual(response.environment, environment)

