"""Jinja2 templating support for web.py applications.
"""
import web
from jinja2 import Environment, FileSystemLoader


_context_processors = []


@web.memoize
def get_jinja_env():
    """Returns the jinja2 environment object.

    The environment object will be created when this function is called for the first time.
    The template search path is taken from `jinja2_template_path` setting from `web.config`.
    """
    path = web.config.get("jinja2_template_path") or "templates"
    return Environment(loader=FileSystemLoader(path))


def render_template(_filename, **kwargs):
    """Renders a template with given filename.

    All the keyword arguments passed to this function are carried to the
    template.
    """
    env = get_jinja_env()
    template = env.get_template(_filename)
    template_vars = _get_injected_vars()
    template_vars.update(kwargs)
    return template.render(**template_vars)


def _get_injected_vars():
    if 'injected_vars' not in web.ctx:
        d = {}
        for cp in _context_processors:
            d.update(cp())
        web.ctx.injected_vars = d
    return web.ctx.injected_vars


def context_processor(f):
    """Decorator to inject new variables automatically into the context
    of a template, like in Flask.

        @context_processor
        def inject_vars():
            return {
                user: get_user()
            }
    """
    _context_processors.append(f)
    return f


def template_filter(name):
    """Decorator to add a template filter.

        @template_filter('uppercase')
        def uppercase_filter(s):
            return s.upper()
    """
    def decorator(f):
        env = get_jinja_env()
        env.filters[name] = f
        return f
    return decorator