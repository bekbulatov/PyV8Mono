import os
from setuptools import setup, Extension

V8_PREFIX = os.environ.get('V8_PREFIX')

if not V8_PREFIX:
    print 'You should set V8_PREFIX variable in the environment'
    exit(1)

V8_LIBRARY_DIR = os.path.join(V8_PREFIX, 'lib64/')
V8_INCLUDE_DIR = os.path.join(V8_PREFIX, 'include/')


setup(
    name='PyV8Mono',
    description='Python binding for V8 MonoContext library',
    version='1.1',
    author='Bekbulatov Alexander',
    author_email='alexander@bekbulatov.ru',
    url='https://github.com/bekbulatov/PyV8Mono',
    packages=['PyV8Mono'],
    ext_modules=[
        Extension('PyV8Mono.monocontext',
            include_dirs=[
                V8_INCLUDE_DIR,
            ],
            library_dirs=[
                V8_LIBRARY_DIR,
            ],
            libraries=[
                'v8monoctx',
            ],
            sources=[
                'monocontext.cpp',
            ],
            extra_link_args=[])
    ])
