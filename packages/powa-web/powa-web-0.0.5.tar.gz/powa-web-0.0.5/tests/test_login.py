from test import TestHandlerBase

# Your TestHandler class
# They are runnable via nosetests as well.
class BasicTest(TestHandlerBase):

    def login_test(self):
        # Example on how to hit a particular handler as POST request.
        # In this example, we want to test the redirect,
        # thus follow_redirects is set to False
        post_args = {'email': 'bro@bro.com'}
        response = self.fetch(
        '/create_something',
        method='POST',
        body=urllib.urlencode(post_args),
        follow_redirects=False)
        # On successful, response is expected to redirect to /tutorial
        self.assertEqual(response.code, 302)
        self.assertTrue(
        response.headers['Location'].endswith('/tutorial'),
        "response.headers['Location'] did not ends with /tutorial"
        )

            Write
            Preview

        Parsed as Markdown Edit in fullscreen

