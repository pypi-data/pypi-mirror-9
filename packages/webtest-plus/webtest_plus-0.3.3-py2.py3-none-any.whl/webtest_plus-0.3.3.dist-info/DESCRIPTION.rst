Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Description: ============
        webtest-plus
        ============
        
        .. image:: https://badge.fury.io/py/webtest-plus.png
            :target: http://badge.fury.io/py/webtest-plus
        
        .. image:: https://travis-ci.org/sloria/webtest-plus.png?branch=master
            :target: https://travis-ci.org/sloria/webtest-plus
        
        An extension of `WebTest <http://webtest.pythonpaste.org/en/latest/>`_  with useful extras, including `requests <http://docs.python-requests.org/en/latest/>`_-style authentication.
        
        Install
        -------
        .. code-block:: bash
        
            $ pip install -U webtest-plus
        
        Usage
        -----
        
        .. code-block:: python
        
            import unittest
            from myapp import app
            from webtest_plus import TestApp
        
            class TestMyApp(unittest.TestCase):
        
                def setUp(self):
                    self.app = TestApp(app)
        
                def test_protected_endpoint(self):
                    response = self.app.get("/secret/", expect_errors=True)
                    assert response.status_code == 401
                    # Requests-style authentication
                    response = self.app.get("/secret/", auth=("admin", "passw0rd"))
                    assert response.status_code == 200
        
                def test_more_secrets(self):
                    # Another way to authenticate
                    self.app.authenticate(username="admin", password="passw0rd")
                    assert self.app.get("/secret/").status_code == 200
                    self.app.deauthenticate()
                    assert self.app.get("/secret/", expect_errors=True).status_code == 401
        
                def test_posting_json(self):
                    # Testing json requests and responses
                    response = self.app.post_json("/postsecret/", {"secret": "myprecious"},
                                                    auth=("admin", "passw0rd"))
                    assert response.request.content_type == "application/json"
        
                def test_clicking(self):
                    response = self.app.get("/")
                    response = response.click("Protected link", auth=("admin", "passw0rd"))
                    assert response.status_code == 200
        
                def test_token_auth(self):
                    response = self.app.get('/secret-requires-token/', expect_errors=True)
                    assert response.status_code == 401
        
                    # Authenticate with JWT
                    response = self.app.get('/secret-requires-token',
                        auth='yourlongtokenhere', auth_type='jwt')
                    assert response.status_code == 200
        
        
        
        Features
        --------
        
        * Basic HTTP authentication
        * `JSON Web Token <https://openid.net/specs/draft-jones-json-web-token-07.html>`_ authentication
        * Auto-follow redirects
        * Framework-agnostic
        
        Requirements
        ------------
        
        - Python >= 2.6 or >= 3.3
        
        License
        -------
        
        MIT licensed. See the bundled `LICENSE <https://github.com/sloria/webtest-plus/blob/master/LICENSE>`_ file for more details.
        
        
        Changelog
        ---------
        
        0.3.3 (2015-03-17)
        ++++++++++++++++++
        
        * Implement ``TestApp.head``.
        
        0.3.2 (2014-06-04)
        ++++++++++++++++++
        
        * Bug fix that caused an ``UnboundLocalError``.
        
        0.3.1 (2014-05-31)
        ++++++++++++++++++
        
        * Fix string encoding bug on Python 2.
        
        0.3.0 (2014-05-31)
        ++++++++++++++++++
        
        * Add support for JSON web token authentication.
        
        0.2.1 (2013-11-24)
        ++++++++++++++++++
        
        * Add authentication to ``TestResponse.click`` and ``TestResponse.clickbutton``.
        
        0.2.0 (2013-10-15)
        ++++++++++++++++++
        
        * Add support for JSON methods (e.g. ``app.post_json``, etc.)
        
        0.1.0 (2013-10-06)
        ++++++++++++++++++
        
        * First release.
        * HTTP Basic Authentication working.
        
Keywords: wsgi test unit tests web testing http
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Topic :: Internet :: WWW/HTTP :: WSGI
Classifier: Topic :: Internet :: WWW/HTTP :: WSGI :: Server
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
