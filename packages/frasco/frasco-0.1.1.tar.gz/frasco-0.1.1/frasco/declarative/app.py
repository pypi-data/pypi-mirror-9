import os
import sys
import yaml
from ..app import Frasco
from ..actions import load_actions, load_grouped_actions, Context
from ..utils import import_string, logger, deep_update_dict
from ..signals import signal
from ..views import Blueprint
from .loaders import FeaturesLoader, ActionsLoader, ViewsLoader, ServicesLoader
from flask.helpers import get_root_path
from flask import render_template
from jinja2 import FileSystemLoader


class DeclarativeFrasco(Frasco):
    def __new__(cls, import_name, **kwargs):
        decl_kwargs = {k: kwargs.pop(k) for k in kwargs.keys() if k in
                        ('config_filename', 'view_folder', 'feature_folder',
                         'action_folder')}
        factory = DeclarativeFrascoFactory(**decl_kwargs)
        return factory.create_app(import_name, **kwargs)


class DeclarativeFrascoFactory(object):
    """Creates an app from the given configuration file. Will load features, actions
    and blueprints relative to the configuration file
    """

    def __init__(self, config_filename="app.yml", view_folder="views",
                 feature_folder="features", action_folder="actions"):
        self.config_filename = config_filename
        self.view_folder = view_folder
        self.feature_folder = feature_folder
        self.action_folder = action_folder

    def create_app(self, import_name, **kwargs):
        app = Frasco(import_name, **kwargs)
        self.setup_app(app)
        return app

    def setup_app(self, app):
        self.configure_app(app, False)
        self.load_actions((app))
        self.load_services(app)
        self.load_blueprints(app)

    def configure_app(self, app, with_feature_blueprints=True, env=None):
        config_path = os.path.join(app.root_path, self.config_filename)
        view_path = os.path.join(app.root_path, self.view_folder)
        feature_path = os.path.join(app.root_path, self.feature_folder)

        app.jinja_loader.loaders.insert(0, FileSystemLoader(view_path))
        app.view_folder = self.view_folder
        app.config.from_yaml(config_path)

        env = env or os.environ.get("FRASCO_ENV") or "prod"
        filename, ext = os.path.splitext(config_path)
        env_filename = filename + "-" + env + ext
        app.config['ENV'] = env
        if os.path.exists(env_filename):
            with open(env_filename) as f:
                env_conf = yaml.load(f.read())
            app.config.deep_update(env_conf)

        if "INCLUDE_FILES" in app.config:
            for spec in app.config["INCLUDE_FILES"]:
                if not isinstance(spec, dict):
                    spec = {"filename": spec}
                app.config.from_yaml(spec["filename"],
                    deep_update=spec.get("deep_update", False))

        if os.path.exists(feature_path):
            sys.path.insert(0, feature_path)
        loader = FeaturesLoader()
        for feature in loader.load(app):
            app.register_feature(feature, with_blueprints=with_feature_blueprints)
            feature.init_declarative(app)

        if "ERROR_HANDLERS" in app.config:
            for code, template in app.config["ERROR_HANDLERS"].iteritems():
                self.register_error_handler(app, code, template)

        if "BEFORE_REQUEST_ACTIONS" in app.config:
            app.request_actions.extend(load_actions(app.config["BEFORE_REQUEST_ACTIONS"], 'before'))
        if "AFTER_REQUEST_ACTIONS" in app.config:
            app.request_actions.extend(load_actions(app.config["AFTER_REQUEST_ACTIONS"], 'after'))

        for listener in app.config.get("SIGNAL_LISTENERS", []):
            actions = load_grouped_actions(listener)
            def callback(sender, **kwargs):
                with Context(kwargs):
                    actions.execute()
            signal(listener["name"]).connect(callback, weak=False)

        for fqdn in app.config.get("IMPORTS", []):
            import_string(fqdn)

    def register_error_handler(self, app, code, template):
        @app.errorhandler(code)
        def func(error):
            return render_template(template, error=error), code

    def load_actions(self, app):
        action_path = os.path.join(app.root_path, self.action_folder)
        action_package = self.action_folder.replace("/", ".")
        if os.path.exists(action_path):
            loader = ActionsLoader(action_path, pypath=action_package)
            for action in loader.load(app):
                app.actions.register(action)

    def load_services(self, app):
        loader = ServicesLoader(os.path.join(app.root_path, "services"))
        for service in loader.load(app):
            app.register_service(service)

    def load_blueprints(self, app):
        view_path = os.path.join(app.root_path, self.view_folder)
        view_package = self.view_folder.replace("/", ".")
        if os.path.exists(view_path):
            loader = ViewsLoader(view_path, pypath=view_package)
            for obj in loader.load(app):
                if isinstance(obj, Blueprint):
                    app.register_blueprint(obj)
                else:
                    app.add_view(obj)

        for feature in app.features:
            feature.init_blueprints(app)