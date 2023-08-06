""" Muffin-Jade -- Jade template engine for Muffin framework. """

import asyncio
from os import path as op

from pyjade.ext.html import pyjade, Compiler, local_context_manager
from pyjade.nodes import Extends, CodeBlock

from muffin.plugins import BasePlugin
from muffin.utils import to_coroutine


__version__ = "0.0.4"
__project__ = "muffin-jade"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


class Plugin(BasePlugin):

    """ The class is used to control the pyjade integration to Muffin application. """

    name = 'jade'
    defaults = dict(
        cache_size=100,
        encoding='UTF-8',
        pretty=True,
        template_folder='templates',
    )

    def __init__(self, **options):
        """ Initialize the plugin. """
        super().__init__(**options)

        self.env = Environment()
        self.providers = []
        self.functions = {}

    def setup(self, app):
        """ Setup the plugin from an application. """
        super().setup(app)

        self.ctx_provider(lambda: {'app': self.app})
        self.env = Environment(debug=app.cfg.DEBUG, **self.options)

    def ctx_provider(self, func):
        """ Decorator for adding a context provider.

        ::
            @jade.ctx_provider
            def my_context():
                return {...}
        """
        func = to_coroutine(func)
        self.providers.append(func)
        return func

    def register(self, func):
        """ Register function to templates. """
        if callable(func):
            self.functions[func.__name__] = func
        return func

    @asyncio.coroutine
    def render(self, path, **context):
        """ Render a template with context. """
        funcs = self.functions
        ctx = dict(self.functions, jdebug=lambda: dict(
            (k, v) for k, v in ctx.items() if k not in funcs and k != 'jdebug'))
        for provider in self.providers:
            _ctx = yield from provider()
            ctx.update(_ctx)
        ctx.update(context)
        template = self.env.get_template(path)
        return self.env.render(template, **ctx)


class ExtendCompiler(Compiler):

    """ Jade Compiler which supports include and extend tags. """

    def __init__(self, node, env, **options):
        """ Initialize the compiler. """
        super(ExtendCompiler, self).__init__(node, **options)
        self.env = env
        self.blocks = {node.name: node for node in self.node.nodes if isinstance(node, CodeBlock)}
        while self.node.nodes and isinstance(self.node.nodes[0], Extends):
            compiler = self.env.get_template(self.node.nodes[0].path)
            self.node = compiler.node
            for cblock in compiler.blocks.values():
                if cblock.name in self.blocks:
                    sblock = self.blocks[cblock.name]
                    if sblock.mode == 'prepend':
                        sblock.nodes = sblock.nodes + cblock.nodes
                    elif sblock.mode == 'append':
                        sblock.nodes = cblock.nodes + sblock.nodes
                else:
                    self.blocks[cblock.name] = cblock

    def visitCodeBlock(self, block):
        """ Support block interihance. """
        block = self.blocks.get(block.name, block)
        for node in block.nodes:
            self.visitNode(node)

    def visitInclude(self, node):
        """ Support inclusion. """
        compiler = self.env.get_template(node.path)
        self.visit(compiler.node)


class Environment(object):

    """ Template's environment. """

    cache = {}
    cache_index = []

    def __init__(self, **options):
        """ Prepare an environment. """
        self.options = options

    @classmethod
    def clean(cls):
        """ Clean self templates' cache. """
        cls.cache = {}
        cls.cache_index = []

    def load_template(self, path):
        """ Load and compile a template. """
        if not path.startswith('/'):
            path = op.join(self.options['template_folder'], path)

        with open(path, 'rb') as f:
            source = f.read().decode(self.options['encoding'])

        return ExtendCompiler(
            pyjade.parser.Parser(source).parse(), pretty=self.options['pretty'],
            env=self, compileDebug=True
        )

    def cache_template(self, path):
        """ Cache a compiled template. """
        compiler = self.load_template(path)
        if path not in self.cache_index:
            self.cache_index.append(path)
        self.cache[path] = compiler
        if len(self.cache_index) > self.options['cache_size']:
            self.cache.pop(self.cache_index.pop(0))
        return compiler

    def get_template(self, path):
        """ Load template from cache. """
        if not self.options['debug'] and self.options['cache_size']:
            return self.cache.get(path, self.cache_template(path))

        return self.load_template(path)

    @staticmethod
    def render(compiler, **context):
        """ Render the template with the context. """
        with local_context_manager(compiler, context):
            return compiler.compile()

# pylama:ignore=E1002,E0203
