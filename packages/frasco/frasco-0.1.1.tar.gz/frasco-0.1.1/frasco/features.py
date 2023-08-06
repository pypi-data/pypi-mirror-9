from .actions import ActionRegistry, ActionFunction
from .commands import CommandDecorator
from .utils import RequirementMissingError
from werkzeug.local import LocalProxy
from flask import current_app
import click
import inspect
import functools


class FeatureError(Exception):
    pass


class Feature(object):
    """A feature configures an app and bundles actions.
    Can also register blueprints.
    """
    name = None
    # Name of other features which this one requires
    requires = None
    # Default options
    defaults = None
    # A list of Action classes
    actions = None
    # A list of blueprint instances that will be registered on the app
    blueprints = None
    # A list of click commands that will be registered on the app
    commands = None
    # Group commands declared using the @command() on members of this class
    # under a command group. This value can be the group name which would be
    # replaced with an instance of click.Group at instanciation or a click.Group object.
    # If False, no group will be used and commands will be added to the commands
    # attribute
    command_group = None
    # A list of hooks
    hooks = None
    # ignore some attributes when looking for annotations
    ignore_attributes = None

    def __init__(self, options=None, **kwargs):
        if not self.name:
            raise FeatureError("A name property must be defined on Feature classes")
        self.options = dict(self.defaults or {})
        if options is not None:
            self.options.update(options)
        self.options.update(kwargs)
        self.actions = ActionRegistry(self.actions)

        # We only do attribute discovery at instanciation time
        # because we want decorators used on methods to be bound
        # on the instance
        commands = []
        for name in dir(self):
            if name == "__class__" or (self.ignore_attributes is not None and name in self.ignore_attributes):
                continue
            attr = getattr(self, name)
            # Adds function decorated with @command to commands
            if isinstance(attr, CommandDecorator):
                commands.append(attr.as_command())
                attr = attr.unbound_func
            # Adds function decorated with @action to actions
            if isinstance(attr, ActionFunction):
                self.actions.register(attr)
            # Adds function decorator with @hook to hooks
            elif hasattr(attr, 'hooks'):
                if self.hooks is None:
                    self.hooks = []
                self.hooks.append((attr, attr.hooks))

        if commands:
            if not self.commands:
                self.commands = []
            if self.command_group is None or isinstance(self.command_group, str):
                name = self.command_group or self.name
                self.command_group = click.Group(name=name, help=inspect.getdoc(self))
            if self.command_group:
                for cmd in commands:
                    self.command_group.add_command(cmd)
                self.commands.append(self.command_group)
            else:
                self.commands.extend(commands)

    def init_app(self, app):
        pass

    def init_declarative(self, app):
        pass

    def init_blueprints(self, app):
        if self.blueprints:
            for bp in self.blueprints:
                kwargs = {}
                if isinstance(bp, tuple):
                    bp, kwargs = bp
                if inspect.isclass(bp):
                    bp = bp()
                elif callable(bp):
                    bp = bp(app)
                app.register_blueprint(bp, **kwargs)
                app.feature_blueprint_names.add(bp.name)


class FeatureRegistry(object):
    def __init__(self):
        self.features = {}

    def register(self, feature):
        self.features[feature.name] = feature

    def names(self):
        return self.features.keys()

    def exists(self, name):
        return name in self.features

    def __getitem__(self, name):
        if name not in self.features:
            raise RequirementMissingError("Missing feature '%s'" % name)
        return self.features[name]

    def __getattr__(self, name):
        return self[name]

    def __contains__(self, name):
        return name in self.features

    def __iter__(self):
        return self.features.itervalues()

    def __len__(self):
        return len(self.features)


def get_current_app_feature(name):
    return current_app.features[name]


_feature_proxies = {}

def feature_proxy(name):
    if name not in _feature_proxies:
        _feature_proxies[name] = LocalProxy(lambda: get_current_app_feature(name))
    return _feature_proxies[name]


def pass_feature(*feature_names):
    """Injects a feature instance into the kwargs
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for name in feature_names:
                kwargs[name] = feature_proxy(name)
            return f(*args, **kwargs)
        return wrapper
    return decorator