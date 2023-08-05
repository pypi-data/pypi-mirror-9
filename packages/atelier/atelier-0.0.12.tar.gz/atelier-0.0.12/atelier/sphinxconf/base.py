# -*- coding: utf-8 -*-
# Copyright 2011-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.
"""

Basic extension

Sphinx setup used to build the Lino documentation.

Thanks to 

- `Creating reStructuredText Directives 
  <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_





"""

from __future__ import print_function
# from __future__ import unicode_literals
# removed 20140604 because it causes:
# File "/home/luc/repositories/sphinx/sphinx/application.py", line 548, in add_object_type
#     'doc_field_types': doc_field_types})
# TypeError: type() argument 1 must be string, not unicode


import os
import inspect
from unipath import Path

from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.nodes import split_explicit_title
from sphinx import addnodes

from importlib import import_module
from atelier.utils import i2d


def autodoc_skip_member(app, what, name, obj, skip, options):
    defmod = getattr(obj, '__module__', None)
    if defmod is not None:
        if defmod.startswith('django.'):
            return True
    if name == 'Q':
        print(20141219, app, what, name, obj, skip, options)
    if name != '__builtins__':
        #~ print 'autodoc_skip_member', what, repr(name), repr(obj)

        if what == 'class':
            if name.endswith('MultipleObjectsReturned'):
                return True
            if name.endswith('DoesNotExist'):
                return True

            #~ if isinstance(obj,ObjectDoesNotExist) \
              #~ or isinstance(obj,MultipleObjectsReturned):
                #~ return True

    #~ if what == 'exception':
        #~ print 'autodoc_skip_member',what, repr(name), repr(obj), skip
        #~ return True

    return skip


SRCREF_TEMPLATE_AFTER = """

(This module's source code is available `here <%s>`__.)

"""

#~ """
#~ SIDEBAR = """
#~ (source code: :srcref:`/%s`)

#~ """

SIDEBAR = """
(`source code <%s>`__)

"""

#~ SIDEBAR = """
#~ .. sidebar:: Use the source, Luke

  #~ We generally recommend to also consult the source code.
  #~ This module's source code is available at
  #~ :srcref:`/%s.py`

#~ """


def autodoc_add_srcref(app, what, name, obj, options, lines):
    if what == 'module':
        s = srcref(obj)
        if s:
            if True:  # after 20150111
                lines += (SRCREF_TEMPLATE_AFTER % s).splitlines()
            else:
                s = (SIDEBAR % s).splitlines()
                s.reverse()
                for ln in s:
                    lines.insert(0, ln)


def get_blog_url(env, today):
    """
    Return the URL to your developer blog entry of that date.
    """
    if today.year < 2013:  # TODO: make this configurable
        blogger_project = "lino"
        url_root = "http://code.google.com/p/%s/source/browse/" % blogger_project
        parts = ('docs', 'blog', str(today.year), today.strftime("%m%d.rst"))
        return url_root + "/".join(parts)

    fmt = env.settings.get('blogref_format')
    if not fmt:
        return "oops"
        raise Exception(
            "Please set your `blogref_format` to something "
            "like 'http://www.example.com/blog/%Y/%m%d.html'")
    url = today.strftime(fmt)
    return url


def blogref_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Inserts a reference to the blog entry of the specified date.
    
    Instead of writing ``:doc:`/blog/2011/0406```
    it is better to write ``:blogref:`20110406```
    because the latter works between Sphinx trees and also supports archived blog entries.
    
    """
    # thanks to http://docutils.sourceforge.net/docs/howto/rst-roles.html
    # this code originally from roles.pep_reference_role
    #~ print 20130315, rawtext, text, utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    try:
        date = i2d(int(target))
    except ValueError:
        msg = inliner.reporter.error(
            'Invalid text %r: must be an integer date of style "20130315" .'
            % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    #~ print repr(env)
    #~ raise Exception(20130315)
    #~ ref = inliner.document.settings.pep_base_url
           #~ + inliner.document.settings.pep_file_url_template % date)
    roles.set_classes(options)
    #~ from django.conf import settings
    #~ shown_text = settings.SITE.dtos(date)
    env = inliner.document.settings.env
    if not has_explicit_title:
        title = date.strftime(env.settings.get('today_fmt', '%Y-%m-%d'))
    title = utils.unescape(title)
    return [nodes.reference(rawtext, title,
                            refuri=get_blog_url(env, date),
                            **options)], []


def srcref(mod):
    """Return the `source file name` for usage by Sphinx's ``srcref``
    role.  Returns None if the source file is empty (which happens
    e.g. for :file:`__init__.py` files whose only purpose is to mark a
    package).

    Examples:
    
    >>> import atelier
    >>> from atelier import sphinxconf
    >>> from atelier.sphinxconf import base
    >>> print(srcref(atelier))
    https://github.com/lsaffre/atelier/blob/master/atelier/__init__.py
    >>> print(srcref(sphinxconf))
    https://github.com/lsaffre/atelier/blob/master/atelier/sphinxconf/__init__.py
    >>> print(srcref(base))
    https://github.com/lsaffre/atelier/blob/master/atelier/sphinxconf/base.py
    
    """
    root_module_name = mod.__name__.split('.')[0]
    root_mod = __import__(root_module_name)
    srcref_url = getattr(root_mod, 'srcref_url', None)
    if srcref_url is None:
        return
    #~ if not mod.__name__.startswith('lino.'):
        #~ return
    srcref = mod.__file__
    if srcref.endswith('.pyc'):
        srcref = srcref[:-1]
    if os.stat(srcref).st_size == 0:
        return
    #~ srcref = srcref[len(lino.__file__)-17:]
    root = Path(root_mod.__file__).ancestor(2)
    if len(root):
        srcref = srcref[len(root) + 1:]
    srcref = srcref.replace(os.path.sep, '/')
    return srcref_url % srcref


def message_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    node = nodes.literal(rawtext, text)
    return [node], []

def actor_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    node = nodes.literal(rawtext, text)
    return [node], []


def coderef_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    try:
        modname, name = target.rsplit('.', 1)
    except ValueError:
        raise Exception("Don't know how to import name %s" % target)
    mod = import_module(modname)

    try:
        value = getattr(mod, name, None)
    except AttributeError:
        raise Exception("No name '%s' in module '%s'" % (name, modname))
    #~ raise Exception("20130908 %s " % lines)
    if isinstance(value, type):
        if value.__module__ != modname:
            raise Exception("20130908 %r != %r" % (value.__module__, modname))

    url = srcref(mod)

    lines, line_no = inspect.getsourcelines(value)
    if line_no:
        url += "#" + str(line_no)
    if not has_explicit_title:
        pass
    pnode = nodes.reference(title, title, internal=False, refuri=url)
    return [pnode], []


def unused_srcref_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    has_explicit_title, title, target = split_explicit_title(text)
    url = srcref(target)
    try:
        full_url = base_url % part
    except (TypeError, ValueError):
        inliner.reporter.warning(
            'unable to expand %s extlink with base URL %r, please make '
            'sure the base contains \'%%s\' exactly once'
            % (typ, base_url), line=lineno)
        full_url = base_url + part
    if not has_explicit_title:
        if prefix is None:
            title = full_url
        else:
            title = prefix + part
    pnode = nodes.reference(title, title, internal=False, refuri=full_url)
    return [pnode], []


def command_parse(env, sig, signode):
    # x, y = sig.split()
    signode += addnodes.literal_emphasis(sig, sig)
    # signode += addnodes.literal_strong(sig, sig)  # needs Sphinx >= 1.3
    return sig


def setup(app):
    """
    The Sphinx setup function used for Lino-related documentation trees.
   
    """
    def add(**kw):
        skw = dict()
        for k, v in kw.items():
            skw[str(k)] = str(v)

        app.add_object_type(**skw)

    add(directivename='management_command',
        rolename='manage',
        indextemplate='pair: %s; management command')

    # add(directivename='role', rolename='role',
    #     indextemplate='pair: %s; docutils role')
    # add(directivename='directive', rolename='directive',
    #     indextemplate='pair: %s; docutils directive')

    # add(directivename='fab_command',
    #     rolename='fab',
    #     indextemplate='pair: %s; fab command')

    app.add_object_type(
        'command', 'cmd', 'pair: %s; command', command_parse)

    add(directivename='xfile',
        rolename='xfile',
        indextemplate='pair: %s; file')
    add(directivename='setting', rolename='setting',
        indextemplate='pair: %s; setting')
    add(directivename='actorattr', rolename='aa',
        indextemplate='pair: %s; actor attribute')
    add(directivename='screenshot', rolename='screen',
        indextemplate='pair: %s; screenshot')
    add(directivename='modattr', rolename='modattr',
        indextemplate='pair: %s; model attribute')
    add(directivename='model',
        rolename='model', indextemplate='pair: %s; model')
    #app.connect('build-finished', handle_finished)

    app.connect(str('autodoc-skip-member'), autodoc_skip_member)
    app.connect(str('autodoc-process-docstring'), autodoc_add_srcref)

    app.add_role(str('coderef'), coderef_role)
    app.add_role(str('message'), message_role)
    app.add_role(str('actor'), actor_role)

    roles.register_canonical_role(str('blogref'), blogref_role)

    app.add_config_value(
        'blogref_format',
        "http://www.lino-framework.org/blog/%Y/%m%d.html", 'html')
    # setup2(app)

    # from .dirtables import setup
    # setup(app)

    #~ app.add_directive('screenshot', ScreenshotDirective)
    #~ app.add_config_value('screenshots_root', '/screenshots/', 'html')

    #~ from djangosite.utils import doctest
    #~ doctest.setup(app)


