import functools
import os

import genshi.template.loader as g_loader

def default_extension(loader_func):
    @functools.wraps(loader_func)
    def add_extension(filename):
        name, ext = os.path.splitext(filename)
        ext = ext or '.html'
        filename = name + ext
        return loader_func(filename)
    return add_extension

# Create a loader which will search in the ./templates directory for templates
#  using a default extension.
loader = g_loader.TemplateLoader(
    search_path = [default_extension(g_loader.package(__name__, 'templates'))],
    auto_reload=True,
)

def render(page, context):
    doc = loader.load(page).generate(**context)
    # during rendering, disable stripping of whitespace because the
    # pygments-rendered <pre> is wrapped in a genshi.Markup.
    # http://genshi.edgewall.org/wiki/GenshiFaq#WhatisGenshidoingwiththewhitespaceinmymarkuptemplate
    return doc.render('xhtml', strip_whitespace=False)
