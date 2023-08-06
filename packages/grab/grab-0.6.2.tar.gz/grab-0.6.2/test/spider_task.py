import six

import grab.spider.base
from grab import Grab
from grab.spider import Spider, Task, SpiderMisuseError, NoTaskHandler
from grab.spider import inline_task
from test.util import BaseGrabTestCase, build_grab


class SimpleSpider(Spider):
    base_url = 'http://google.com'

    def task_baz(self, grab, task):
        self.SAVED_ITEM = grab.response.body


class TestSpider(BaseGrabTestCase):
    def setUp(self):
        self.server.reset()

    def test_task_priority(self):
        # Automatic random priority
        grab.spider.base.RANDOM_TASK_PRIORITY_RANGE = (10, 20)
        bot = SimpleSpider(priority_mode='random')
        bot.setup_queue()
        task = Task('baz', url='xxx')
        self.assertEqual(task.priority, None)
        bot.add_task(task)
        self.assertTrue(10 <= task.priority <= 20)

        # Automatic constant priority
        grab.spider.base.DEFAULT_TASK_PRIORITY = 33
        bot = SimpleSpider(priority_mode='const')
        bot.setup_queue()
        task = Task('baz', url='xxx')
        self.assertEqual(task.priority, None)
        bot.add_task(task)
        self.assertEqual(33, task.priority)

        # Automatic priority does not override explictily setted priority
        grab.spider.base.DEFAULT_TASK_PRIORITY = 33
        bot = SimpleSpider(priority_mode='const')
        bot.setup_queue()
        task = Task('baz', url='xxx', priority=1)
        self.assertEqual(1, task.priority)
        bot.add_task(task)
        self.assertEqual(1, task.priority)

        self.assertRaises(SpiderMisuseError,
                          lambda: SimpleSpider(priority_mode='foo'))

    def test_task_url(self):
        bot = SimpleSpider()
        bot.setup_queue()
        task = Task('baz', url='xxx')
        self.assertEqual('xxx', task.url)
        bot.add_task(task)
        self.assertEqual('http://google.com/xxx', task.url)
        self.assertEqual(None, task.grab_config)

        g = Grab(url='yyy')
        task = Task('baz', grab=g)
        bot.add_task(task)
        self.assertEqual('http://google.com/yyy', task.url)
        self.assertEqual('http://google.com/yyy', task.grab_config['url'])

    def test_task_clone(self):
        bot = SimpleSpider()
        bot.setup_queue()

        task = Task('baz', url='xxx')
        bot.add_task(task.clone())

        # Pass grab to clone
        task = Task('baz', url='xxx')
        g = Grab()
        g.setup(url='zzz')
        bot.add_task(task.clone(grab=g))

        # Pass grab_config to clone
        task = Task('baz', url='xxx')
        g = Grab()
        g.setup(url='zzz')
        bot.add_task(task.clone(grab_config=g.config))

    def test_task_clone_with_url_param(self):
        task = Task('baz', url='xxx')
        task.clone(url='http://yandex.ru/')

    def test_task_useragent(self):
        bot = SimpleSpider()
        bot.setup_queue()

        g = Grab()
        g.setup(url=self.server.get_url())
        g.setup(user_agent='Foo')

        task = Task('baz', grab=g)
        bot.add_task(task.clone())
        bot.run()
        self.assertEqual(self.server.request['headers']['User-Agent'], 'Foo')

    def test_task_nohandler_error(self):
        class TestSpider(Spider):
            pass

        bot = TestSpider()
        bot.setup_queue()
        bot.add_task(Task('page', url=self.server.get_url()))
        self.assertRaises(NoTaskHandler, bot.run)

    def test_task_raw(self):
        class TestSpider(Spider):
            def prepare(self):
                self.codes = []

            def task_page(self, grab, task):
                self.codes.append(grab.response.code)

        self.server.response['code'] = 502

        bot = TestSpider(network_try_limit=1)
        bot.setup_queue()
        bot.add_task(Task('page', url=self.server.get_url()))
        bot.add_task(Task('page', url=self.server.get_url()))
        bot.run()
        self.assertEqual(0, len(bot.codes))

        bot = TestSpider(network_try_limit=1)
        bot.setup_queue()
        bot.add_task(Task('page', url=self.server.get_url(), raw=True))
        bot.add_task(Task('page', url=self.server.get_url(), raw=True))
        bot.run()
        self.assertEqual(2, len(bot.codes))

    def test_task_callback(self):
        class TestSpider(Spider):
            def task_page(self, grab, task):
                self.meta['tokens'].append('0_handler')

        class FuncWithState(object):
            def __init__(self, tokens):
                self.tokens = tokens

            def __call__(self, grab, task):
                self.tokens.append('1_func')

        tokens = []
        func = FuncWithState(tokens)

        bot = TestSpider()
        bot.meta['tokens'] = tokens
        bot.setup_queue()
        # classic handler
        bot.add_task(Task('page', url=self.server.get_url()))
        # callback option overried classic handler
        bot.add_task(Task('page', url=self.server.get_url(), callback=func))
        # callback and null task name
        bot.add_task(Task(name=None, url=self.server.get_url(), callback=func))
        # callback and default task name
        bot.add_task(Task(url=self.server.get_url(), callback=func))
        bot.run()
        self.assertEqual(['0_handler', '1_func', '1_func', '1_func'],
                         sorted(tokens))

    def test_inline_task(self):

        def callback(self):
            self.write(self.request.uri)
            self.finish()

        self.server.response['get.callback'] = callback

        server = self.server

        class TestSpider(Spider):
            calls = []
            responses = []

            def add_response(self, grab):
                self.responses.append(grab.doc.unicode_body())

            def task_generator(self):
                url = server.get_url('/?foo=start')
                yield Task('inline', url=url)

            def subroutine_task(self, grab):

                for x in six.moves.range(2):
                    url = server.get_url('/?foo=subtask%s' % x)
                    grab.setup(url=url)
                    grab = yield Task(grab=grab)
                    self.add_response(grab)
                    self.calls.append('subinline%s' % x)

            @inline_task
            def task_inline(self, grab, task):
                self.add_response(grab)
                self.calls.append('generator')

                for x in six.moves.range(3):
                    url = server.get_url('/?foo=%s' % x)
                    grab.setup(url=url)
                    grab = yield Task(grab=grab)

                    self.add_response(grab)
                    self.calls.append('inline%s' % x)

                    grab = yield self.subroutine_task(grab)
                    # In this case the grab body will be the same
                    # as is in subroutine task:  /?foo=subtask1
                    self.add_response(grab)

                url = server.get_url('/?foo=yield')
                self.add_task(Task('yield', url=url))

            def task_yield(self, grab, task):
                self.add_response(grab)
                self.calls.append('yield')

                url = server.get_url('/?foo=end')
                yield Task('end', url=url)

            def task_end(self, grab, task):
                self.add_response(grab)
                self.calls.append('end')

        bot = TestSpider()
        bot.run()

        self.assertEqual(['/?foo=start',
                          '/?foo=0',
                          '/?foo=subtask0', '/?foo=subtask1', '/?foo=subtask1',
                          '/?foo=1',
                          '/?foo=subtask0', '/?foo=subtask1', '/?foo=subtask1',
                          '/?foo=2',
                          '/?foo=subtask0', '/?foo=subtask1', '/?foo=subtask1',
                          '/?foo=yield', '/?foo=end'],
                         bot.responses)
        self.assertEqual(['generator',
                          'inline0',
                          'subinline0', 'subinline1',
                          'inline1',
                          'subinline0', 'subinline1',
                          'inline2',
                          'subinline0', 'subinline1',
                          'yield', 'end'],
                         bot.calls)

    def test_task_url_and_grab_options(self):
        class TestSpider(Spider):
            def setup(self):
                self.done = False

            def task_page(self, grab, task):
                self.done = True

        bot = TestSpider()
        bot.setup_queue()
        g = Grab()
        g.setup(url=self.server.get_url())
        self.assertRaises(SpiderMisuseError, Task,
                          'page', grab=g, url=self.server.get_url())

    def test_task_invalid_name(self):
        self.assertRaises(SpiderMisuseError, Task,
                          'generator', url='http://ya.ru/')

    def test_task_constructor_invalid_args(self):
        # no url, no grab, no grab_config
        self.assertRaises(SpiderMisuseError, Task, 'foo')
        # both url and grab_config
        self.assertRaises(SpiderMisuseError, Task, 'foo',
                          url=1, grab_config=1)
        # both grab and grab_config
        self.assertRaises(SpiderMisuseError, Task, 'foo',
                          grab=1, grab_config=1)

    def test_task_clone_invalid_args(self):
        task = Task('foo', url='http://ya.ru/')
        # both url and grab
        self.assertRaises(SpiderMisuseError, task.clone,
                          url=1, grab=1)
        # both url and grab_config
        self.assertRaises(SpiderMisuseError, task.clone,
                          url=1, grab_config=1)
        # both grab_config and grab
        self.assertRaises(SpiderMisuseError, task.clone,
                          grab=1, grab_config=1)

    def test_task_clone_grab_config_and_url(self):
        g = build_grab()
        g.setup(url='http://foo.com/')
        task = Task('foo', grab=g)
        task2 = task.clone(url='http://bar.com/')
        self.assertEqual(task2.url, 'http://bar.com/')
        self.assertEqual(task2.grab_config['url'], 'http://bar.com/')

    def test_task_clone_kwargs(self):
        g = build_grab()
        g.setup(url='http://foo.com/')
        task = Task('foo', grab=g, cache_timeout=1)
        task2 = task.clone(cache_timeout=2)
        self.assertEqual(2, task2.cache_timeout)

    def test_task_comparison(self):
        t1 = Task('foo', url='http://foo.com/', priority=1)
        t2 = Task('foo', url='http://foo.com/', priority=2)
        t3 = Task('foo', url='http://foo.com/')
        # If both tasks have priorities then task are
        # compared by their priorities
        self.assertTrue(t1 < t2)
        # If any of compared tasks does not have priority
        # than tasks are equal
        self.assertTrue(t1 == t3)
        self.assertTrue(t3 == t3)

    def test_task_get_fallback_handler(self):
        class TestSpider(Spider):
            def zz(self, task):
                pass

            def task_bar_fallback(self, task):
                pass


        t1 = Task('foo', url='http://foo.com/', fallback_name='zz')
        t2 = Task('bar', url='http://foo.com/')
        t3 = Task(url='http://foo.com/')

        bot = TestSpider()

        self.assertEqual(t1.get_fallback_handler(bot), bot.zz)
        self.assertEqual(t2.get_fallback_handler(bot), bot.task_bar_fallback)
        self.assertEqual(t3.get_fallback_handler(bot), None)
