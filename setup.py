import os
from setuptools import setup, Extension, find_packages

V8_PREFIX = os.environ.get('V8_PREFIX')
V8_VERSION = os.environ.get('V8_VERSION')
V8_LIBRARY_DIR = os.path.join(V8_PREFIX, 'lib64/')
V8_INCLUDE_DIR = os.path.join(V8_PREFIX, 'include/')


setup(
    name='PyV8Mono',
    description='Python binding for V8 MonoContext library',
    version='3.00',
    author='Bekbulatov Alexander',
    author_email='alexander@bekbulatov.ru',
    url='https://gitlab.corp.mail.ru/portal/v8monocontext',  # FIXME
    packages=find_packages(),
    py_modules=[],
    ext_modules=[
        Extension('monocontext',
            include_dirs=[
                V8_INCLUDE_DIR,
            ],
            library_dirs=[
                V8_LIBRARY_DIR,
            ],
            libraries=[
		'v8monoctx.%s' % V8_VERSION,
            ],
            sources=[
                'monocontext.cpp',
            ],
            extra_link_args=[])
    ])
