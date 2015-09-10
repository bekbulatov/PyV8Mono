#-*- coding: utf-8 -*-

from monocontext import MonoContext
import logging
import os.path


logger = logging.getLogger(__name__)


def force_bytes(s):
    if isinstance(s, bytes):
        return s
    return s.encode('utf-8')


class FestRenderer(object):
    _js_loaded = False

    def __init__(self, js_root='', js_files=None, js_files_autoload=False, **kwargs):
        self.renderer = MonoContext(**kwargs)
        self.js_root = js_root
        self.js_files = js_files

        if self.js_files_autoload:
            self.load_js_files()

    def load_js_files(self):
        if not self._js_loaded:
            if self.js_files is not None:
                for js_file in self.js_files:
                    filepath = os.path.abspath(os.path.join(self.js_root, js_file))
                    self.renderer.load_file(filepath)
            self._js_loaded = True

    def render(self, template_name, json_str):
        if not self.js_files_autoload:
            self.load_js_files()

        template_name = force_bytes(template_name)
        json_str = force_bytes(json_str)

        try:
            bundle = template_name.split('/')[-2]
        except ValueError:
            raise ValueError('Wrong template name')

        filepath = os.path.abspath(os.path.join(self.js_root, template_name))
        append_str = ';fest["{}.xml"]( JSON.parse(__dataFetch()) );'.format(bundle)
        response, errors = self.renderer.execute_file(filepath, append_str, json_str)
        if errors:
            logger.warning('\n'.join(errors))
        return response
