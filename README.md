# Python binding PyV8Mono

PyV8Mono - python extension for V8 MonoContext library <https://github.com/fsitedev/v8monoctx>.
Commonly intended for rendering `fest` templates <https://github.com/mailru/fest>

# INSTALLATION

First of all install v8monoctx shared library <https://github.com/fsitedev/v8monoctx> and set 
V8_VERSION and V8_PREFIX environment variables, e.g.

	$ export V8_VERSION=3.27.0
	$ export V8_PREFIX=/usr/local/v8-$V8_VERSION

To install this perl module type the following:

	python setup.py build
	sudo -E bash -c 'python setup.py install'


# Usage

	json_str = json.dumps(context)

	renderer = MonoContext()
	# load common js helpers
	renderer.load_file('context/build.js')

	# render templtate
	append_str = ';fest["{}.xml"]( JSON.parse(__dataFetch()) );'.format(bundle)
	response, errors = renderer.execute_file(filepath, append_str, json_str)


# MonoContext options

	GC control:

	run_low_memory_notification. Options for running V8::LowMemoryNotification each N iterations. Disabled if 0 (default).
	run_idle_notification_loop. Options for running V8::IdleNotification each N iterations. Disabled if 0 (default).

	V8 control:

	cmd_args. String of arguments for V8. Ex: '--no_incremental_marking', Default is ''

	Others:

	watch_templates. If set True, MonoContext will check whether templates change by modified date. Useful for development. Default is False
