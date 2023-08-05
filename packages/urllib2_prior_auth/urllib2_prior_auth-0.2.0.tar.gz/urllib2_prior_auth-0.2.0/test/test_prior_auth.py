import sys
# /usr/lib64/python2.7/test/test_urllib2.py
if sys.version_info[0] == 3:
    sys.path = ['/usr/lib64/python3.3', '/usr/lib64/python3.3/plat-linux2',
                '/usr/lib64/python3.3/lib-old',
                '/usr/lib64/python3.3/lib-dynload']
else:
    sys.path = ['/usr/lib64/python2.7', '/usr/lib64/python2.7/plat-linux2',
                '/usr/lib64/python2.7/lib-old',
                '/usr/lib64/python2.7/lib-dynload']
from test.test_urllib2 import MockHTTPSHandler, MockPasswordManager
sys.path.insert(0, '.')

try:
    from urllib.request import Request, OpenerDirector
except ImportError:
    from urllib2 import Request, OpenerDirector

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from urllib2_prior_auth import HTTPBasicPriorAuthHandler

import logging
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.INFO)


class TestPriorHandler(unittest.TestCase):
    def setUp(self):
        pwd_manager = MockPasswordManager()
        pwd_manager.add_password(None, 'https://api.github.com',
                                 'somebody', 'verysecret')
        auth_prior_handler = HTTPBasicPriorAuthHandler(pwd_manager)
        self.verbose_handler = MockHTTPSHandler()

        self.opener = OpenerDirector()
        self.opener.add_handler(self.verbose_handler)
        self.opener.add_handler(auth_prior_handler)

    def test_auth_prior_handler(self):
        req = Request("https://api.github.com")
        self.opener.open(req)
        logging.debug('handler = headers {}'.format(
            self.verbose_handler.httpconn.req_headers))

        self.assertFalse('Authorization' in
                         self.verbose_handler.httpconn.req_headers)


if __name__ == "__main__":
    unittest.main()
