# -*- coding: utf-8 -*-
# Copyright 2011-2014 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""Sphinx setup used to build most of the documentation trees
mainained by myself.


.. toctree::

.. autosummary::
   :toctree:

   insert_input
   refstothis
   sigal_image
   complex_tables
   blog
   base
   dirtables



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

import os
import sys

from unipath import Path

from atelier.projects import load_projects


def configure(globals_dict, settings_module_name=None):
    """Adds to your `conf.py` an arbitrary series of things that all my
    Sphinx docs configuration files have in common.

    To be called from inside the Sphinx `conf.py` as follows::

      from djangosite.utils.sphinxconf import configure
      configure(globals())

    Incomplete list of `conf.py` settings that will be set:

    - `intersphinx_mapping` : The intersphinx entries for projects
       managed in this atelier. Atelier gets this information by
       checking for an attribute `intersphinx_urls` in the global
       namespace of each project's main module.

    - `extensions`
    - `templates_path`
    - `html_static_path`
    - master_doc='index'
    - source_suffix='.rst'
    - primary_domain='py'
    - pygments_style='sphinx'


    """
    filename = globals_dict.get('__file__')
    sys.path.append(Path(filename).parent.absolute())

    globals_dict.update(extensions=[
        'sphinx.ext.autodoc',
        'sphinx.ext.autosummary',
        'sphinx.ext.inheritance_diagram',
        'sphinx.ext.todo',
        'sphinx.ext.extlinks',
        'sphinx.ext.graphviz',
        'sphinx.ext.intersphinx',
        # no i18n, no discovery, only one entry per doc,
        # 'sphinxcontrib.newsfeed',
        #~ 'sphinx.ext.doctest',
        'atelier.sphinxconf.base',
        'atelier.sphinxconf.dirtables',
        'atelier.sphinxconf.refstothis',
        'atelier.sphinxconf.insert_input',
    ])

    # default config for autosummary:
    globals_dict.update(autosummary_generate=True)
    globals_dict.update(autodoc_default_flags=['members'])

    if settings_module_name is not None:
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_module_name

        # Trigger loading of Djangos model cache in order to avoid
        # side effects that would occur when this happens later while
        # importing one of the models modules.
        from django.conf import settings
        settings.SITE.startup()

        globals_dict.update(
            template_bridge=str('atelier.sphinxconf.DjangoTemplateBridge'))

    mydir = Path(__file__).parent.absolute()
    globals_dict.update(templates_path=['.templates', mydir])

    # globals_dict.update(html_static_path=['.static'])

    # some settings i use in all projects:

    globals_dict.update(master_doc='index')
    globals_dict.update(source_suffix='.rst')
    globals_dict.update(primary_domain='py')
    globals_dict.update(pygments_style='sphinx')

    # The following will load the `fabfile.py` of other
    # projects. Possible side effects.

    extlinks = dict(
        linoticket=(
            'http://lino-framework.org/tickets/%s.html',
            'Lino Ticket #'))
    intersphinx_mapping = dict()
    for prj in load_projects():
        prj.load_fabfile()
        for doc_tree in prj.doc_trees:
            p = prj.root_dir.child(doc_tree, '.build', 'objects.inv')
            if p.exists():
                if doc_tree == 'docs':
                    k = prj.nickname
                else:
                    k = prj.nickname + doc_tree.replace('_', '')
                url = prj.intersphinx_urls.get(doc_tree)
                if url:
                    intersphinx_mapping[k] = (url, p)

        if prj.srcref_url:
            k = '%s_srcref' % prj.nickname
            extlinks[str(k)] = (prj.srcref_url, '')

    globals_dict.update(intersphinx_mapping=intersphinx_mapping)
    globals_dict.update(extlinks=extlinks)
    # globals_dict.update(
    #     blogref_format="http://www.lino-framework.org/blog/%Y/%m%d.html")


def version2rst(self, m):
    """
    used in docs/released/index.rst
    """
    v = m.__version__
    if v.endswith('+'):
        v = v[:-1]
        print("The current stable release is :doc:`%s`." % v)
        print("We are working on a future version in the code repository.")
    elif v.endswith('pre'):
        print("We're currently working on :doc:`%s`." % v[:-3])
    else:
        print("The current stable release is :doc:`%s`." % v)
        #~ print("We're currently working on :doc:`coming`.")


from sphinx.jinja2glue import BuiltinTemplateLoader


class DjangoTemplateBridge(BuiltinTemplateLoader):

    """The :meth:`configure` method installs this as `template_bridge
    <http://sphinx-doc.org/config.html#confval-template_bridge>`_ for
    Sphinx.  It causes a template variable ``settings`` to be added
    the Sphinx template context. This cannot be done using
    `html_context
    <http://sphinx-doc.org/config.html#confval-html_context>`_ because
    Django settings are not pickleable.

    """

    def render(self, template, context):
        from django.conf import settings
        context.update(settings=settings)
        return super(DjangoTemplateBridge, self).render(template, context)

    def render_string(self, source, context):
        from django.conf import settings
        context.update(settings=settings)
        return super(DjangoTemplateBridge, self).render_string(source, context)


