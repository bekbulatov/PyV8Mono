#-*- coding: utf-8 -*-

from monocontext import MonoContext, V8Error
import unittest


JS_FILE = 'data/js'
ABSENT_JS_FILE = '/tmp/nonexistent.js'
JSON_FILE = 'data/json'
ZERO_JS_FILE = 'data/zero_embed'


class MonoContextTestCase(unittest.TestCase):

    def setUp(self):
        with open(JSON_FILE) as f:
            self.json_str = f.read()

    def test_load_file(self):
        # Load file
        renderer = MonoContext()
        self.assertEqual([], renderer.load_file(JS_FILE))

        # No existent error file
        self.assertRaises(V8Error, renderer.load_file, ABSENT_JS_FILE)

    def test_execute_file(self):
        renderer = MonoContext()

        # Execute file with no append not json
        out, errors = renderer.execute_file(JS_FILE, '', '')
        self.assertEqual(0, len(out))

        # Execute file with append
        out, errors = renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', '{}')  # TODO: передавать пустую строку вместо json
        self.assertEqual(31478, len(out))

        # Execute file with append and json
        out, errors = renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)
        self.assertEqual(551294, len(out))

        # Execute file with append and json again
        out, errors = renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)
        self.assertEqual(551294, len(out))

        # Execute file with append and json again
        out, errors = renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)
        self.assertEqual(551294, len(out))

        # Check \0 embeded symbol
        out, errors = renderer.execute_file(ZERO_JS_FILE, '', '')
        self.assertEqual(11, len(out))

        # No existent error file
        self.assertRaises(V8Error, renderer.execute_file, ABSENT_JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Catch warn message from __errorLog
        out, errors = renderer.execute_file(JS_FILE, '__errorLog("123");', self.json_str)
        self.assertEqual(['123'], errors)

    def test_init(self):
        # Init w/o parameters
        renderer = MonoContext()
        renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Init with LowMemoryNotification
        renderer = MonoContext(run_low_memory_notification=10)
        renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Init with IdleNotification
        renderer = MonoContext(run_idle_notification_loop=10)
        renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Init with watch_templates
        renderer = MonoContext(watch_templates=True)
        renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Init cmd_args
        renderer = MonoContext(cmd_args='--max-old-space-size=128')
        renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Init with all parameters
        renderer = MonoContext(run_low_memory_notification=5, run_idle_notification_loop=10, watch_templates=True)
        renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Wrong init
        self.assertRaises(TypeError, MonoContext, run_low_memory_notification='7')

        self.assertRaises(ValueError, MonoContext, cmd_args='--max-old-space-size=128 ' * 200)


if __name__ == '__main__':
    unittest.main()
