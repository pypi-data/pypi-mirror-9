from tornado.testing import AsyncHTTPTestCase

# import your app module
from powa import make_app

# Create your Application for testing
# In this example, the tornado config file is located in: APP_ROOT/config/test.py
app = make_app()

# Create your base Test class.
# Put all of your testing methods here.
class TestHandlerBase(AsyncHTTPTestCase):
    def setUp(self):
        super(TestHandlerBase, self).setUp()

    def get_app(self):
        return app # this is the global app that we created above.

    def get_http_port(self):
        return options.port
