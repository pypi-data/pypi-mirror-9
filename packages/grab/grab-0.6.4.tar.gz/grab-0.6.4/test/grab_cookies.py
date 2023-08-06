# coding: utf-8
import json
from grab import Grab
from grab.error import GrabMisuseError
from grab.cookie import CookieManager, create_cookie
import pickle

from test.util import TMP_FILE, build_grab
from test.util import BaseGrabTestCase


class TestCookies(BaseGrabTestCase):
    def setUp(self):
        self.server.reset()

    def test_parsing_response_cookies(self):
        g = build_grab()
        self.server.response['cookies'] = {'foo': 'bar', '1': '2'}.items()
        g.go(self.server.get_url())
        self.assertEqual(g.response.cookies['foo'], 'bar')

    def test_multiple_cookies(self):
        g = build_grab()
        self.server.response['cookies'] = []
        g.setup(cookies={'foo': '1', 'bar': '2'})
        g.go(self.server.get_url())
        self.assertEqual(
            set(map(lambda item: item.strip(),
                    self.server.request['headers']['Cookie'].split('; '))),
            set(['foo=1', 'bar=2']))

    def test_session(self):
        # Test that if Grab gets some cookies from the server
        # then it sends it back
        g = build_grab()
        g.setup(reuse_cookies=True)
        self.server.response['cookies'] = {'foo': 'bar'}.items()
        g.go(self.server.get_url())
        self.assertEqual(g.response.cookies['foo'], 'bar')
        g.go(self.server.get_url())
        self.assertEqual(self.server.request['headers']['Cookie'], 'foo=bar')
        g.go(self.server.get_url())
        self.assertEqual(self.server.request['headers']['Cookie'], 'foo=bar')

        # Test reuse_cookies=False
        g = build_grab()
        g.setup(reuse_cookies=False)
        self.server.response['cookies'] = {'foo': 'baz'}.items()
        g.go(self.server.get_url())
        self.assertEqual(g.response.cookies['foo'], 'baz')
        g.go(self.server.get_url())
        self.assertTrue(len(self.server.request['cookies']) == 0)

        # Test something
        g = build_grab()
        g.setup(reuse_cookies=True)
        self.server.response['cookies'] = {'foo': 'bar'}.items()
        g.go(self.server.get_url())
        self.assertEqual(g.response.cookies['foo'], 'bar')
        g.clear_cookies()
        g.go(self.server.get_url())
        self.assertTrue(len(self.server.request['cookies']) == 0)

    def test_redirect_session(self):
        g = build_grab()
        self.server.response['cookies'] = {'foo': 'bar'}.items()
        g.go(self.server.get_url())
        self.assertEqual(g.response.cookies['foo'], 'bar')

        # Setup one-time redirect
        g = build_grab()
        self.server.response['cookies'] = {}
        self.server.response_once['headers'] = [
            ('Location', self.server.get_url()),
            ('Set-Cookie', 'foo=bar'),
        ]
        self.server.response_once['code'] = 302
        g.go(self.server.get_url())
        self.assertEqual(self.server.request['cookies']['foo'].value, 'bar')

    def test_load_dump(self):
        g = build_grab()
        cookies = {'foo': 'bar', 'spam': 'ham'}
        g.setup(cookies=cookies)
        g.go(self.server.get_url())
        g.dump_cookies(TMP_FILE)
        self.assertEqual(set(cookies.items()),
                         set((x['name'], x['value'])
                             for x in json.load(open(TMP_FILE))))

        # Test non-ascii
        g = build_grab()
        cookies = {'foo': 'bar', 'spam': u'бегемот'}
        g.setup(cookies=cookies)
        g.go(self.server.get_url())
        g.dump_cookies(TMP_FILE)
        self.assertEqual(set(cookies.items()),
                         set((x['name'], x['value'])
                             for x in json.load(open(TMP_FILE))))

        # Test load cookies
        g = build_grab()
        cookies = [{'name': 'foo', 'value': 'bar'},
                   {'name': 'spam', 'value': u'бегемот'}]
        json.dump(cookies, open(TMP_FILE, 'w'))
        g.load_cookies(TMP_FILE)
        self.assertEqual(set(g.cookies.items()),
                         set((x['name'], x['value']) for x in cookies))

    def test_cookiefile(self):
        g = build_grab()

        # Empty file should not raise Exception
        open(TMP_FILE, 'w').write('')
        g.setup(cookiefile=TMP_FILE)
        g.go(self.server.get_url())

        cookies = [{'name': 'spam', 'value': 'ham'}]
        json.dump(cookies, open(TMP_FILE, 'w'))

        # One cookie are sent in server reponse
        # Another cookies is passed via the `cookiefile` option
        self.server.response['cookies'] = {'godzilla': 'monkey'}.items()
        g.setup(cookiefile=TMP_FILE, debug=True)
        g.go(self.server.get_url())
        self.assertEqual(self.server.request['cookies']['spam'].value, 'ham')

        # This is correct reslt of combining two cookies
        MERGED_COOKIES = [('godzilla', 'monkey'), ('spam', 'ham')]

        # g.cookies should contains merged cookies
        self.assertEqual(set(MERGED_COOKIES),
                         set(g.cookies.items()))

        # `cookiefile` file should contains merged cookies
        self.assertEqual(set(MERGED_COOKIES),
                         set((x['name'], x['value'])
                             for x in json.load(open(TMP_FILE))))

        # Just ensure it works
        g.go(self.server.get_url())

    def test_manual_dns(self):
        import pycurl

        g = build_grab()
        g.transport.curl.setopt(pycurl.RESOLVE,
                                ['foo:%d:127.0.0.1' % self.server.port])
        self.server.response['get.data'] = 'zzz'
        g.go('http://foo:%d/' % self.server.port)
        self.assertEqual(b'zzz', g.response.body)

    def test_different_domains(self):
        import pycurl

        g = build_grab()
        names = [
            'foo:%d:127.0.0.1' % self.server.port,
            'bar:%d:127.0.0.1' % self.server.port,
        ]
        g.transport.curl.setopt(pycurl.RESOLVE, names)

        self.server.response['cookies'] = {'foo': 'foo'}.items()
        g.go('http://foo:%d' % self.server.port)
        self.assertEqual(dict(g.response.cookies.items()), {'foo': 'foo'})

        self.server.response['cookies'] = {'bar': 'bar'}.items()
        g.go('http://bar:%d' % self.server.port)
        self.assertEqual(dict(g.response.cookies.items()), {'bar': 'bar'})

    def test_cookie_domain(self):
        import pycurl

        g = Grab()
        names = [
            'example.com:%d:127.0.0.1' % self.server.port,
        ]
        g.transport.curl.setopt(pycurl.RESOLVE, names)
        g.cookies.set('foo', 'bar', domain='example.com')
        g.go('http://example.com:%d/' % self.server.port)

    def test_update_invalid_cookie(self):
        g = build_grab()
        self.assertRaises(GrabMisuseError, g.cookies.update, None)
        self.assertRaises(GrabMisuseError, g.cookies.update, 'asdf')
        self.assertRaises(GrabMisuseError, g.cookies.update, ['asdf'])

    def test_from_cookie_list(self):
        cookie = create_cookie('foo', 'bar')
        mgr = CookieManager.from_cookie_list([cookie])
        test_cookie = [x for x in mgr.cookiejar if x.name == 'foo'][0]
        self.assertEqual(cookie.name, test_cookie.name)

        mgr = CookieManager.from_cookie_list([])
        self.assertEqual(0, len(list(mgr.cookiejar)))

    def test_pickle_serialization(self):
        cookie = create_cookie('foo', 'bar')
        mgr = CookieManager.from_cookie_list([cookie])
        dump = pickle.dumps(mgr)
        mgr2 = pickle.loads(dump)
        self.assertEqual(list(mgr.cookiejar)[0].value,
                         list(mgr2.cookiejar)[0].value)

    def test_get_item(self):
        cookie = create_cookie('foo', 'bar')
        mgr = CookieManager.from_cookie_list([cookie])
        self.assertEqual('bar', mgr['foo'])
        self.assertRaises(KeyError, lambda: mgr['zzz'])
