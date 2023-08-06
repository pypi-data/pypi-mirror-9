# -*- coding: utf-8 -*-
"""
    weppy_haml.ext
    --------------

    Provides the Haml extension for weppy

    :copyright: (c) 2014 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import os
import codecs
from weppy.extensions import Extension, TemplateExtension
from .hamlpy import Compiler
from .cache import HamlCache


def _read_source(filepath):
    return codecs.open(filepath, 'r', encoding='utf-8').read()


def _process_template(source):
    compiler = Compiler()
    return compiler.process_lines(source.splitlines())


def _store_compiled(filepath, code):
    outfile = codecs.open(filepath+".html", 'w', encoding='utf-8')
    outfile.write(code)


class Haml(Extension):
    namespace = 'Haml'
    default_config = dict(
        set_as_default=False,
        auto_reload=False
    )

    def _load_config(self):
        self.config.set_as_default = self.config.get(
            'set_as_default', self.default_config['set_as_default'])
        self.config.auto_reload = self.config.get(
            'auto_reload', self.default_config['auto_reload'])

    def on_load(self):
        self._load_config()
        self.env.debug = lambda: self.app.debug
        self.env.cache = HamlCache()
        self.app.add_template_extension(HamlTemplate)
        if self.config.set_as_default:
            self.app.template_default_extension = '.haml'
        for path, dirs, files in os.walk(self.app.template_path):
            for fname in files:
                if os.path.splitext(fname)[1] == ".haml":
                    filepath = os.path.join(path, fname)
                    source = _read_source(filepath)
                    code = _process_template(source)
                    _store_compiled(filepath, code)
                    if self.config.auto_reload:
                        relname = filepath.split(self.app.template_path+"/")[1]
                        self.env.cache.set(relname, source, code)


class HamlTemplate(TemplateExtension):
    namespace = 'Haml'
    file_extension = '.haml'

    def preload(self, path, name):
        if self.config.auto_reload or self.env.debug():
            filepath = os.path.join(path, name)
            source = _read_source(filepath)
            code = self.env.cache.get(name, source)
            if not code:
                code = _process_template(source)
                _store_compiled(filepath, code)
                self.env.cache.set(name, source, code)
        return path, name+".html"
