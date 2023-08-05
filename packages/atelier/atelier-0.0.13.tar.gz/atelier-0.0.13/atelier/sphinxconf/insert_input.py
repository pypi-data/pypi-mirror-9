# -*- coding: utf-8 -*-
# Copyright 2011-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Defines the :class:`InsertInputDirective` class and some
subclasses, installing the following directives:

- :rst:dir:`py2rst`
- :rst:dir:`django2rst`


.. rst:directive:: py2rst

Executes the Python code, capturing the `stdout` and inserting it to
the document, parsing it as reStructuredText.

For example, if you write::

  .. py2rst::

      url = 'http://planet.python.org/'
      print("`This <%s>`_ is my *favourite* planet." % url)

then you get:

.. py2rst::

  url = 'http://planet.python.org/'
  print("`This <%s>`_ is my *favourite* planet." % url)

Note that when the Sphinx builder is running under Python 2.7, the
following future imports have been done::

  from __future__ import print_function
  from __future__ import unicode_literals



"""

from __future__ import print_function
from __future__ import unicode_literals

"""Note: the `import unicode_literals` caused the following::

    Traceback (most recent call last):
      File "/home/luc/pythonenvs/py27/local/lib/python2.7/site-packages/sphinx/cmdline.py", line 245, in main
        warningiserror, tags, verbosity, parallel)
      File "/home/luc/pythonenvs/py27/local/lib/python2.7/site-packages/sphinx/application.py", line 122, in __init__
        self.config.setup(self)
      File "/home/luc/hgwork/atelier/atelier/sphinxconf/__init__.py", line 654, in setup
        indextemplate='pair: %s; management command')
      File "/home/luc/pythonenvs/py27/local/lib/python2.7/site-packages/sphinx/application.py", line 503, in add_object_type
        'doc_field_types': doc_field_types})
    TypeError: type() argument 1 must be string, not unicode
    
I solved this by a manual patch in line 308 of 
:file:`sphinx/application.py`::
    
    def import_object(self, objname, source=None):
        objname = str(objname)  # LS 20140108 accept unicode strings
        # needed when calling from Python 2.7 with
        # `from __future__ import unicode_literals`
        try:
            module, name = objname.rsplit('.', 1)
        except ValueError, err:
    

"""


import logging
logger = logging.getLogger(__name__)

import sys
from StringIO import StringIO

from docutils import nodes
from docutils import statemachine
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles

#~ class ScreenshotDirective(directives.images.Image):
    #~ """
    #~ Directive to insert a screenshot.
    #~ """
    #~ def run(self):
        #~ assert len(self.arguments) == 1
        # ~ # name = '/../gen/screenshots/' + self.arguments[0]
        #~ name = '/gen/screenshots/' + self.arguments[0]
        #~ self.arguments = [name]
        #~ (image_node,) = directives.images.Image.run(self)
        #~ return [image_node]


class InsertInputDirective(Directive):
    """
    Base class for directives that work by generating rst markup
    to be forwarded to `state_machine.insert_input()`.
    """
    titles_allowed = False
    has_content = True
    raw_insert = False
    option_spec = {
        'language': directives.unchanged_required,
        'debug': directives.flag,
    }

    def get_rst(self):
        "Override this to return a string in rst syntax"
        raise NotImplementedError()

    def run(self):

        self.env = self.state.document.settings.env
        self.language = self.options.get('language', self.env.config.language)
        self.env.temp_data['language'] = self.language

        # catch exceptions and report them together with the name of
        # the guilty file
        try:
            output = self.get_rst()
        except Exception as e:
            import traceback
            traceback.print_exc(e)
            document = self.state.document
            return [document.reporter.warning(str(e), line=self.lineno)]

        #~ output = output.decode('utf-8')

        if 'debug' in self.options:
            print(self.env.docname)
            print('-' * 50)
            print(output)
            print('-' * 50)

        content = statemachine.StringList(output.splitlines())

        if self.raw_insert:

            self.state_machine.insert_input(content, output)
            return []

        if self.titles_allowed:
            node = nodes.section()
            # necessary so that the child nodes get the right source/line set
            node.document = self.state.document
            nested_parse_with_titles(self.state, content, node)
        else:
            node = nodes.paragraph()
            node.document = self.state.document
            self.state.nested_parse(content, self.content_offset, node)

        # following lines originally copied from
        # docutils.parsers.rst.directives.tables.RSTTable
        #~ title, messages = self.make_title()
        # ~ node = nodes.Element()          # anonymous container for parsing
        #~ self.state.nested_parse(content, self.content_offset, node)
        #~ if len(node) != 1 or not isinstance(node[0], nodes.table):
            #~ error = self.state_machine.reporter.error(
                #~ 'Error parsing content block for the "%s" directive: exactly '
                #~ 'one table expected.' % self.name, nodes.literal_block(
                #~ self.block_text, self.block_text), line=self.lineno)
            #~ return [error]
        #~ return [x for x in node]
        return list(node)

        #~ table_node = node[0]
        #~ table_node['classes'] += self.options.get('class', [])
        #~ return [table_node]


class Py2rstDirective(InsertInputDirective):

    """Implements the :rst:dir:`py2rst` directive."""

    titles_allowed = True
    has_content = True

    def get_context(self):
        context = dict()
        context.update(self=self)
        context.update(env=self.state.document.settings.env)
        return context

    def get_rst(self):
        if not self.content:
            warning = self.state_machine.reporter.warning(
                'Content block expected for the "%s" directive; none found.'
                % self.name, nodes.literal_block(
                    self.block_text, self.block_text), line=self.lineno)
            return [warning]

        #~ raise Exception("20130331 %r" % self.content)
        code = '\n'.join(self.content)
        return self.output_from_exec(code)

    def output_from_exec(self, code):
        old = sys.stdout
        buffer = StringIO()
        sys.stdout = buffer
        context = self.get_context()

        exec(code, context)

        sys.stdout = old
        s = buffer.getvalue()
        #~ print 20130331, type(s)
        return s

    def shell_block(self, cmd):
        """Run the given command and insert a :rst:dir:`code-block` directive
        which displays both the command and its output.

        For example, if your `.rst` document contains::

            .. py2rst::

                self.shell_block(["echo", "Hello", "world!"])
            
        Then it will be rendered as:

        .. py2rst::

            self.shell_block(["echo", "Hello", "world!"])
        
        This uses the `subprocess.check_output
        <https://docs.python.org/2/library/subprocess.html#subprocess.check_output>`_
        method and the security warnings apply.
        
        If the command returns with a non-zero exit code, the
        exception is catched and converted into a warning.

        """
        print(".. code-block:: bash")
        print()
        import subprocess
        print("    $ " + ' '.join(cmd))
        for ln in subprocess.check_output(cmd).splitlines():
            print("    " + ln)


#~ class DjangoTableDirective(InsertInputDirective):
    #~ def get_rst(self):
        #~ assert len(self.content) == 1
        #~ code = '\n'.join(self.content)
        #~ from django.conf import settings
        #~ print .jobs.Candidatures.request(limit=5).to_rst()
        #~ code = """
        #~ """
        #~ old = sys.stdout
        #~ buffer = StringIO()
        #~ sys.stdout = buffer
        #~ context = dict()
        #~ context.update(settings.SITE.modules)
        #~ context = dict(settings=settings)
        #~ exec(code,context)
        #~ sys.stdout = old
        #~ return buffer.getvalue()


# class BlogNoteDirective(Py2rstDirective):

#     def get_rst(self):
#         return '\n'.join(self.content)


def setup(app):
    # also used by `vor/conf.py`
    app.add_directive(str('py2rst'), Py2rstDirective)

