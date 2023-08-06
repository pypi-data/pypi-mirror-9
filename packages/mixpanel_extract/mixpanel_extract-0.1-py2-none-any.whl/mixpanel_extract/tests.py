import unittest

import mock


class Mixpanel(unittest.TestCase):

    @mock.patch('mixpanel_extract.time')
    def test_make_signed_url(self, m_time):
        from mixpanel_extract import make_signed_url

        m_time.time.return_value = 1425959905.621636

        resp = make_signed_url('BASE',
                               'key1',
                               'secret1',
                               param='value')

        expected = ('BASE?api_key=key1&sig=0f944e40f86507c63e0bc2e18c0f4658'
                    '&param=value&expire=1425963505')
        self.assertEqual(resp, expected)

    @mock.patch('mixpanel_extract.urllib2')
    @mock.patch('mixpanel_extract.time')
    def test_extract_to_fp(self, m_time, m_urllib2):
        from mixpanel_extract import extract_to_fp

        m_urlopen_resp = mock.Mock()
        m_urllib2.urlopen.side_effect = [m_urlopen_resp]

        resp = extract_to_fp('key', 'secret', 'from', 'to')

        expected = ('https://data.mixpanel.com/api/2.0/export/?from_date=from&'
                    'api_key=key&sig=a01519d142fb0d4b5afa926e1a58e82d&'
                    'to_date=to&expire=3601')
        m_urllib2.urlopen.assert_called_once_with(expected)

        self.assertEqual(resp, m_urlopen_resp.fp)

    @mock.patch('mixpanel_extract.urllib2')
    @mock.patch('mixpanel_extract.time')
    def test_extract_to_fp_retry(self, m_time, m_urllib2):
        from mixpanel_extract import extract_to_fp

        m_urlopen_resp = mock.Mock()
        m_urllib2.urlopen.side_effect = [Exception("Failed!"), m_urlopen_resp]

        resp = extract_to_fp('key', 'secret', 'from', 'to')

        expected = ('https://data.mixpanel.com/api/2.0/export/?from_date=from&'
                    'api_key=key&sig=a01519d142fb0d4b5afa926e1a58e82d&'
                    'to_date=to&expire=3601')
        m_urllib2.urlopen.assert_has_calls(
            [mock.call(expected), mock.call(expected)])

        m_time.sleep.assert_called_once_with(60)

        self.assertEqual(resp, m_urlopen_resp.fp)

    @mock.patch('mixpanel_extract.urllib2')
    @mock.patch('mixpanel_extract.time')
    def test_extract_to_fp_retry_fail(self, m_time, m_urllib2):
        from mixpanel_extract import extract_to_fp

        m_urllib2.urlopen.side_effect = [Exception("Failed!")]  # it loops!

        with self.assertRaises(Exception):
            extract_to_fp('key', 'secret', 'from', 'to')

        expected = ('https://data.mixpanel.com/api/2.0/export/?from_date=from&'
                    'api_key=key&sig=a01519d142fb0d4b5afa926e1a58e82d&'
                    'to_date=to&expire=3601')
        m_urllib2.urlopen.assert_has_calls([
            mock.call(expected), mock.call(expected), mock.call(expected),
            mock.call(expected), mock.call(expected)])

        m_time.sleep.assert_has_calls([
            mock.call(60), mock.call(60), mock.call(60), mock.call(60)])
