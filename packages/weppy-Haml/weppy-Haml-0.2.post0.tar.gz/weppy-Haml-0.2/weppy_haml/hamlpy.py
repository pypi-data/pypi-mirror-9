# -*- coding: utf-8 -*-
"""
    weppy_haml.hamlpy
    -----------------

    Adapted from the original code (https://github.com/jessemiller/HamlPy)

    :copyright: (c) 2011 Jesse Miller
    :license: BSD, see LICENSE for more details.
"""

from .nodes import RootNode, HamlNode, create_node

VALID_EXTENSIONS = ['haml', 'hamlpy']


class Compiler:
    def __init__(self, options_dict=None):
        options_dict = options_dict or {}
        self.debug_tree = options_dict.pop('debug_tree', False)
        self.options_dict = options_dict

    def process(self, raw_text):
        split_text = raw_text.split('\n')
        return self.process_lines(split_text)

    def process_lines(self, haml_lines):
        root = RootNode(**self.options_dict)
        line_iter = iter(haml_lines)

        haml_node = None
        for line_number, line in enumerate(line_iter):
            node_lines = line

            if not root.parent_of(HamlNode(line)).inside_filter_node():
                if line.count('{') - line.count('}') == 1:
                    start_multiline = line_number # For exception handling

                    while line.count('{') - line.count('}') != -1:
                        try:
                            line = line_iter.next()
                        except StopIteration:
                            raise Exception('No closing brace found for multi-line HAML beginning at line %s' % (start_multiline+1))
                        node_lines += line

            # Blank lines
            if haml_node is not None and len(node_lines.strip()) == 0:
                haml_node.newlines += 1
            else:
                haml_node = create_node(node_lines)
                if haml_node:
                    root.add_node(haml_node)

        if self.options_dict and self.options_dict.get('debug_tree'):
            return root.debug_tree()
        else:
            return root.render()
