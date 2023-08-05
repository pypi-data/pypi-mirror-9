from unittest import TestCase
from urlparse import parse_qs

from mock import patch


class TestTasks(TestCase):

    @patch('urllib2.urlopen')
    def test_pageview(self, mock_request):
        mock_request.return_value = True

        from unicore.google.tasks import pageview
        pageview('profile-id', 'client-id', {
            'path': 'foo',
            'user_agent': 'user agent',
            'uip': 'the-ip',
            'dr': 'referrer',
            'dh': 'domain',
        })
        mock_request.assert_called()
        (args, kwargs) = mock_request.call_args
        (request,) = args

        self.assertEqual(request.headers, {
            'User-agent': 'user agent',
        })

        data = parse_qs(request.data)
        self.assertEqual(data, {
            'dh': ['domain'],
            'cid': ['client-id'],
            'uip': ['the-ip'],
            'v': ['1'],
            't': ['pageview'],
            'tid': ['profile-id'],
            'dr': ['referrer'],
            'dp': ['foo'],
        })
