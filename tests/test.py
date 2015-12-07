#-*- coding: utf-8 -*-

from PyV8Mono.monocontext import MonoContext, V8Error
import os.path
import time
import unittest


bin_path = os.path.abspath(os.path.dirname(__file__))

JS_FILE = os.path.join(bin_path, '../data/tpl.js')
ZERO_JS_FILE = os.path.join(bin_path, '../data/zero.js')
ERROR_JS_FILE = os.path.join(bin_path, '../data/error.js')
TMP_JS_FILE = os.path.join(bin_path, '../data/tmp.js')
ABSENT_JS_FILE = '/tmp/nonexistent.js'

JSON_FILE = os.path.join(bin_path, '../data/data.json')


class MonoContextTestCase(unittest.TestCase):

    def setUp(self):
        with open(JSON_FILE) as f:
            self.json_str = f.read()

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

    def test_load_file(self):
        # Load file
        renderer = MonoContext()
        self.assertEqual([], renderer.load_file(JS_FILE))

        # Load absent file
        self.assertRaises(V8Error, renderer.load_file, ABSENT_JS_FILE)

    def test_execute_file(self):
        renderer = MonoContext()

        # Execute file with no append not json
        out, errors = renderer.execute_file(JS_FILE, '', '')
        self.assertEqual(0, len(out))

        # Execute file with append
        out, errors = renderer.execute_file(JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', '{}')
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

        # Execute file with js error
        self.assertRaises(V8Error, renderer.execute_file, ERROR_JS_FILE, '', '')

        # Execute absent file
        self.assertRaises(V8Error, renderer.execute_file, ABSENT_JS_FILE, ';fest["top.xml"]( JSON.parse(__dataFetch()) );', self.json_str)

        # Catch warn message from __errorLog
        out, errors = renderer.execute_file(JS_FILE, '__errorLog("123");', self.json_str)
        self.assertEqual(['123'], errors)


class WatchTemplatesTestCase(unittest.TestCase):

    def setUp(self):
        self.js1 = 'function fn() { return 1;}'
        self.js2 = 'function fn() { return 2;}'

    def test_load_file_wt(self):
        renderer = MonoContext(watch_templates=True)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js1)

        renderer.load_file(TMP_JS_FILE)
        out, errors = renderer.execute_file(JS_FILE, ';fn();', '')
        self.assertEqual('1', out)

        time.sleep(1)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js2)

        out, errors = renderer.execute_file(JS_FILE, ';fn();', '')
        self.assertEqual('2', out)

    def test_load_file_no_wt(self):
        renderer = MonoContext(watch_templates=False)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js1)

        renderer.load_file(TMP_JS_FILE)
        out, errors = renderer.execute_file(JS_FILE, ';fn();', '')
        self.assertEqual('1', out)

        time.sleep(1)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js2)

        out, errors = renderer.execute_file(JS_FILE, ';fn();', '')
        self.assertEqual('1', out)

    def test_execute_file_wt(self):
        renderer = MonoContext(watch_templates=True)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js1)
        out, errors = renderer.execute_file(TMP_JS_FILE, ';fn();', '')
        self.assertEqual('1', out)

        time.sleep(1)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js2)
        out, errors = renderer.execute_file(TMP_JS_FILE, ';fn();', '')
        self.assertEqual('2', out)

    def test_execute_file_no_wt(self):
        renderer = MonoContext(watch_templates=False)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js1)
        out, errors = renderer.execute_file(TMP_JS_FILE, ';fn();', '')
        self.assertEqual('1', out)

        time.sleep(1)

        with open(TMP_JS_FILE, 'w') as f:
            f.write(self.js2)
        out, errors = renderer.execute_file(TMP_JS_FILE, ';fn();', '')
        self.assertEqual('1', out)

    def tearDown(self):
        os.unlink(TMP_JS_FILE)


if __name__ == '__main__':
    unittest.main()
