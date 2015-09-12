# PyV8Mono

PyV8Mono - python extension for [V8 MonoContext](https://github.com/fsitedev/v8monoctx) library.
Commonly intended for rendering [fest templates](<https://github.com/mailru/fest>).

## Install

Install v8monoctx following instructions on <https://github.com/fsitedev/v8monoctx>, don't forget to set `V8_PREFIX` environment variables, e.g.

	$ export V8_VERSION=3.27.0
	$ export V8_PREFIX=/usr/local/v8-$V8_VERSION

Then install python module as usual:

	$ python setup.py build
	$ sudo -E bash -c 'python setup.py install'

## MonoContext

MonoContext is low-level wrapper above v8monoctx. It contains 2 main methods:

- `load_file` loads js helpers in V8.

- `execute_file` renders template. It takes template name, suffix for calling template function and context in JSON format. MonoContext will compile template in V8, as `load_file` does.

### Usage

	from PyV8Mono.monocontext import MonoContext
	import json

	renderer = MonoContext(watch_templates=True)

	# load common js helpers
	renderer.load_file('context/build.js')

	# render templtate
	append_str = ';fest["news-detail.xml"]( JSON.parse(__dataFetch()) );'
	json_str = json.dumps(context)
	html, errors = renderer.execute_file("news-detail/news-detail.xml.js", append_str, json_str)

### MonoContext init options

Garbage collector control:

- `run_low_memory_notification`. Options for running `V8::LowMemoryNotification` each N iterations. Disabled if 0 (default). `run_low_memory_notification = 100` will send notification each 100 renders.
- `run_idle_notification_loop`. Options for running `V8::IdleNotification` each N iterations. Disabled if 0 (default).

V8 control:

- `cmd_args`. String of arguments for V8. Ex: `--no_incremental_marking`, Default is ''.

Other:

- `watch_templates`. If set True, MonoContext checks whether template has changed. Useful for development. Default is False.

## FestRenderer

FestRenderer provides more convinient use in your project than MonoContext.

Usually you should have one instance on FestRenderer/MonoContext which stores compiled templates in V8 memory. Also be careful if you load common js utils in master process of your web server, it may cause segfaults.

	from PyV8Mono.renderer import FestRenderer

	renderer = FestRenderer(
		js_root='/path/to/templates/',
		js_files=('context/build.js',),
		js_files_autoload=False
	)
	json_str = json.dumps(context)
	html = renderer.render('news-detail/news-detail.xml.js', json_str)
