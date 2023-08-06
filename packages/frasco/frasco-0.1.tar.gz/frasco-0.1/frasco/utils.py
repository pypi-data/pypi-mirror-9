from werkzeug.utils import import_string as wz_import_string
from werkzeug.local import LocalProxy
from flask import (url_for, Markup, json, request, _request_ctx_stack,\
                   has_request_context)
import imp
import functools
import re
from slugify import slugify
import logging
import yaml
import speaklater
import os
from contextlib import contextmanager


logger = logging.getLogger("frasco")
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


class RequirementMissingError(Exception):
    pass


class ClassBoundDecoratorMixin(object):
    def _wrap_func(self, func):
        @functools.wraps(func)
        def bound_func(*args, **kwargs):
            return self._call_func(func, *args, **kwargs)
        bound_func.unbound_func = func
        return bound_func

    def _call_func(self, func, *args, **kwargs):
        if not hasattr(self, "obj") or self.obj is None:
            return func(*args, **kwargs)
        return func(self.obj, *args, **kwargs)

    def __get__(self, obj, cls):
        self.obj = obj
        return self


def import_string(impstr, attr=None):
    """Imports a string. Can import an attribute of the imported
    class/module using a double colon as a separator
    """
    if "::" in impstr:
        impstr, attr = impstr.split("::")
    imported = wz_import_string(impstr)
    if attr is not None:
        return getobjpath(imported, attr)
    return imported


def getobjpath(obj, path):
    """Returns an item or attribute of the object recursively.
    Item names are specified between brackets, eg: [item].
    Attribute names are prefixed with a dot (the first one is optional), eg: .attr
    Example: getobjpath(obj, "attr1.attr2[item].attr3")
    """
    if not path:
        return obj
    if path.startswith("["):
        item = path[1:path.index("]")]
        return getobjpath(obj[item], path[len(item) + 2:])
    if path.startswith("."):
        path = path[1:]
    if "." in path or "[" in path:
        dot_idx = path.find(".")
        bracket_idx = path.find("[")
        if dot_idx == -1 or bracket_idx < dot_idx:
            idx = bracket_idx
            next_idx = idx
        else:
            idx = dot_idx
            next_idx = idx + 1
        attr = path[:idx]
        return getobjpath(getattr(obj, attr), path[next_idx:])
    return getattr(obj, path)


def find_classes_in_module(module, clstypes):
    """Find classes of clstypes in module
    """
    classes = []
    for item in dir(module):
        item = getattr(module, item)
        try:
            for cls in clstypes:
                if issubclass(item, cls) and item != cls:
                    classes.append(item)
        except Exception as e:
            pass
    return classes


def remove_yaml_frontmatter(source, return_frontmatter=False):
    """If there's one, remove the YAML front-matter from the source
    """
    if source.startswith("---\n"):
        frontmatter_end = source.find("\n---\n", 4)
        if frontmatter_end == -1:
            frontmatter = source
            source = ""
        else:
            frontmatter = source[0:frontmatter_end]
            source = source[frontmatter_end + 5:]
        if return_frontmatter:
            return (source, frontmatter)
        return source
    if return_frontmatter:
        return (source, None)
    return source


def parse_yaml_frontmatter(source):
    source, frontmatter = remove_yaml_frontmatter(source, True)
    if frontmatter:
        return (yaml.load(frontmatter), source)
    return (None, source)


def populate_obj(obj, attrs):
    """Populates an object's attributes using the provided dict
    """
    for k, v in attrs.iteritems():
        setattr(obj, k, v)


def copy_extra_feature_options(feature, target, prefix=""):
    for k, v in feature.options.iteritems():
        if not feature.defaults or k not in feature.defaults:
            target["%s%s" % (prefix, k.upper())] = v


def url_for_static(filename, **kwargs):
    """Shortcut function for url_for('static', filename=filename)
    """
    return url_for('static', filename=filename, **kwargs)


def url_for_same(**overrides):
    return url_for(request.endpoint, **dict(dict(request.args,
        **request.view_args), **overrides))


def wrap_in_markup(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return Markup(f(*args, **kwargs))
    return wrapper


def deep_update_dict(a, b):
    for k, v in b.iteritems():
        if k not in a:
            a[k] = v
        elif isinstance(a[k], dict) and isinstance(v, dict):
            deep_update_dict(a[k], v)
        elif isinstance(a[k], list) and isinstance(v, list):
            a[k].extend(v)
        elif isinstance(v, list) and not isinstance(a[k], list):
            a[k] = [a[k]] + v
        else:
            a[k] = v


class DictObject(object):
    def __init__(self, dct):
        for k, v in dct.iteritems():
            setattr(self, k, v)


class AttrDict(dict):
    """Dict which keys are accessible as attributes
    """
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def get_or_raise(self, name, message):
        try:
            return self[name]
        except KeyError:
            raise KeyError(message)


class JSONEncoder(json.JSONEncoder):
    """A JSONEncoder which always activates the for_json feature
    """
    def __init__(self, *args, **kwargs):
        kwargs["for_json"] = True
        super(JSONEncoder, self).__init__(*args, **kwargs)

    def default(self, o):
        if isinstance(o, speaklater._LazyString):
            return o.value
        if isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)


reloader_extra_dirs = ["actions", "features", "views", "services"]


def get_reloader_extra_files(root='.'):
    extra_files = []
    for filename in os.listdir(root):
        pathname = os.path.join(root, filename)
        if os.path.isdir(pathname) and filename in reloader_extra_dirs:
            for path, _, filenames in os.walk(pathname):
                for f in filenames:
                    if f.endswith('.html') or f.endswith('.yml'):
                        extra_files.append(os.path.join(path, f))
        elif filename.endswith('.yml'):
            extra_files.append(pathname)
    return extra_files


class ContextStack(object):
    def __init__(self, top=None):
        self.stack = []
        self.top = top

    def push(self, item):
        self.stack.append(self.top)
        self.top = item
        return item

    def pop(self):
        self.top = self.stack.pop()

    @contextmanager
    def ctx(self, item):
        self.push(item)
        try:
            yield item
        finally:
            self.pop()

    def make_proxy(self):
        return LocalProxy(lambda: self.top)

    def make_context_mixin(self):
        class ContextMixin(object):
            def __enter__(s):
                self.push(s)
                return s
            def __exit__(s, exc_type, exc_val, exc_tb):
                self.pop()
                return False
        return ContextMixin


def context_stack_on_request_context(name, cls=ContextStack):
    def _get_object():
        if has_request_context() and not hasattr(_request_ctx_stack.top, name):
            setattr(_request_ctx_stack.top, name, cls())
        return getattr(_request_ctx_stack.top, name, None)
    return LocalProxy(_get_object)