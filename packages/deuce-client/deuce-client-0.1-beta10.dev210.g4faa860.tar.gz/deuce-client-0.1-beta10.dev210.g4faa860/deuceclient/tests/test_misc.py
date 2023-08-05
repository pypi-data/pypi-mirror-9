from urllib import parse as parse
import unittest

from deuceclient.utils.misc import set_qs_on_url


class TestMisc(unittest.TestCase):

    def test_set_qs_on_url(self):

        url = 'http://whatever:8080/hello/world'
        params = {
            'param1': 'value1',
            'param2': 'value2'
        }

        ret_url = set_qs_on_url(url, params)
        parts = parse.urlparse(ret_url)
        qs = parse.parse_qs(parts.query)

        self.assertEqual(qs['param1'][0], 'value1')
        self.assertEqual(qs['param2'][0], 'value2')
