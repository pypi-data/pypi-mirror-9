# -*- coding: utf-8 -*-
import os
from jinja2 import Environment, BaseLoader, TemplateNotFound, escape

from logya.compat import quote_plus, is3
from logya.compat import file_open as open


def filesource(logya_inst, name, lines=None):
    """Read and return source of text files.

    A template function that reads the source of the given file and returns it.
    The text is escaped so it can be rendered safely on a Web page.
    The lines keyword argument is used to limit the number of lines returned.

    A use case is for documentation projects to show the source code used
    to render the current example.
    """

    fname = os.path.join(logya_inst.dir_current, name)
    with open(fname, 'r') as f:
        if lines is None:
            content = f.read()
        else:
            content = ''.join(f.readlines()[:lines])
    if not is3:
        content = content.decode('utf-8')
    return escape(content)


def get_doc(logya_inst, url):
    return logya_inst.docs_parsed.get(url)


class Template():
    """Class to handle templates."""

    def __init__(self, logya_inst):
        """Initialize template environment."""

        self.vars = {}
        self.doc_vars = {}
        self.dir_templates = logya_inst.dir_templates
        self.env = Environment(loader=TemplateLoader(self.dir_templates))

        # add urlencode filter to template
        self.env.filters['urlencode'] = lambda x: quote_plus(x.encode('utf-8'))

        # add filesource global to allow for including the source of a file
        self.env.globals['filesource'] = lambda x, lines=None: filesource(
            logya_inst, x, lines=lines)

        self.env.globals['get_doc'] = lambda x: get_doc(logya_inst, x)

    def get_env(self):
        """Return template environment."""

        return self.env

    def add_var(self, name, value):
        """Add to template variables."""

        self.vars[name] = value

    def add_doc_var(self, name, value):
        """Add to template variables."""

        self.doc_vars[name] = value

    def empty_doc_vars(self):
        """Empty doc_vars dictionary."""

        self.doc_vars = {}

    def get_var(self, name):
        """Return value of template variables with given name."""

        return self.vars[name]

    def get_vars(self):
        """Return non doc-specific template variables."""

        return self.vars

    def get_all_vars(self):
        """Return all template variables combined."""

        all_vars = self.vars.copy()
        all_vars.update(self.doc_vars)
        return all_vars


class TemplateLoader(BaseLoader):

    """Class to handle template Loading."""

    def __init__(self, path):
        """Set template path."""

        self.path = path

    def get_source(self, environment, template):
        """Set template source."""

        path = os.path.join(self.path, template)
        if not os.path.exists(path):
            raise TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
            if not is3:
                source = source.decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)