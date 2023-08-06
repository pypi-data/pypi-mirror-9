from test_server import TestServer
import six

from grab import Grab
from grab.spider import Spider, Task
from test.util import BaseGrabTestCase, TEST_SERVER_PORT

ADDRESS = '127.0.0.1'
EXTRA_PORT1 = TEST_SERVER_PORT + 1
EXTRA_PORT2 = TEST_SERVER_PORT + 2
PROXY1 = '%s:%d' % (ADDRESS, TEST_SERVER_PORT)
PROXY2 = '%s:%d' % (ADDRESS, EXTRA_PORT1)
PROXY3 = '%s:%d' % (ADDRESS, EXTRA_PORT2)


class SimpleSpider(Spider):
    def prepare(self):
        self.ports = set()

    def task_baz(self, grab, task):
        print(grab.request_headers)
        self.ports.add(int(grab.response.headers.get('Listen-Port', 0)))


class TestSpider(BaseGrabTestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = TestServer(port=TEST_SERVER_PORT, address=ADDRESS,
                                extra_ports=[EXTRA_PORT1, EXTRA_PORT2])
        cls.server.start()

    def test_setup_proxylist(self):
        content = '%s\n%s\n%s' % (PROXY1, PROXY2, PROXY3)
        open('/tmp/__proxy.txt', 'w').write(content)

        # Simple test, one task
        bot = SimpleSpider(thread_number=1)
        bot.load_proxylist('/tmp/__proxy.txt', 'text_file')
        bot.setup_queue()
        bot.add_task(Task('baz', grab=Grab(url='http://yandex.ru',
                          debug=True)))
        bot.run()

        self.assertEqual(self.server.request['headers']['host'], 'yandex.ru')
        self.assertTrue(len(bot.ports) == 1)

        # By default auto_change is True
        bot = SimpleSpider(thread_number=1)
        bot.load_proxylist('/tmp/__proxy.txt', 'text_file')
        bot.setup_queue()
        for x in six.moves.range(10):
            bot.add_task(Task('baz', 'http://yandex.ru'))
        bot.run()

        self.assertEqual(self.server.request['headers']['host'], 'yandex.ru')
        self.assertTrue(len(bot.ports) > 1)

        # DO the same test with load_proxylist method
        bot = SimpleSpider(thread_number=1)
        bot.load_proxylist('/tmp/__proxy.txt', 'text_file')
        bot.setup_queue()
        for x in six.moves.range(10):
            bot.add_task(Task('baz', 'http://yandex.ru'))
        bot.run()

        self.assertEqual(self.server.request['headers']['host'], 'yandex.ru')
        self.assertTrue(len(bot.ports) > 1)

        # Disable auto_change
        # By default auto_init is True
        bot = SimpleSpider(thread_number=1)
        bot.load_proxylist('/tmp/__proxy.txt', 'text_file', auto_change=False)
        bot.setup_queue()
        for x in six.moves.range(10):
            bot.add_task(Task('baz', 'http://yandex.ru'))
        bot.run()

        self.assertEqual(self.server.request['headers']['host'], 'yandex.ru')
        self.assertTrue(len(bot.ports) == 1)

        # Disable auto_change
        # Disable auto_init
        # Proxylist will not be used by default
        bot = SimpleSpider(thread_number=1)
        bot.load_proxylist('/tmp/__proxy.txt', 'text_file',
                           auto_change=False, auto_init=False)
        bot.setup_queue()
        for x in six.moves.range(10):
            bot.add_task(Task('baz', self.server.get_url()))
        bot.run()

        self.assertEqual(self.server.request['headers'].get('host'),
                         '%s:%s' % (ADDRESS, self.server.port))
        self.assertTrue(len(bot.ports) == 1)
        self.assertEqual(list(bot.ports)[0], self.server.port)

    def test_setup_grab(self):
        # Simple test, one task
        bot = SimpleSpider(thread_number=1)
        bot.setup_grab(proxy=PROXY1)
        bot.setup_queue()
        bot.add_task(Task('baz', 'http://yandex.ru'))
        bot.run()

        self.assertEqual(self.server.request['headers']['host'], 'yandex.ru')
        self.assertEqual(bot.ports, set([self.server.port]))
        self.assertTrue(len(bot.ports) == 1)

        content = '%s\n%s' % (PROXY1, PROXY2)
        open('/tmp/__proxy.txt', 'w').write(content)

        # If proxy is configured with both methods
        # (setup_grab and load_proxylist)
        # then proxylist has priority
        bot = SimpleSpider(thread_number=1)
        bot.load_proxylist('/tmp/__proxy.txt', 'text_file')
        bot.setup_queue()
        for x in six.moves.range(10):
            bot.add_task(Task('baz', 'http://yandex.ru'))
        bot.setup_grab(proxy=PROXY3)
        bot.run()

        self.assertEqual(self.server.request['headers']['host'], 'yandex.ru')
        self.assertTrue(EXTRA_PORT2 not in bot.ports)
