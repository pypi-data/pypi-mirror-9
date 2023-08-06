import click
import sys
import os
from flask.cli import FlaskGroup, ScriptInfo, shell_command
from ..declarative import DeclarativeFrasco
from .run import run_command, start_command, serve_command
from .planet import planet_command
from .scaffold import init_command, gen_command


class FrascoScriptInfo(ScriptInfo):
    @property
    def env(self):
        return os.environ.get("FRASCO_ENV", "prod")

    def load_app(self):
        if self.create_app is None and self.app_import_path is None:
            if os.path.exists("app.py"):
                self.app_import_path = "app"
            elif os.path.exists("app.yml"):
                self.create_app = lambda i: DeclarativeFrasco("__main__", root_path=os.getcwd())
        return super(FrascoScriptInfo, self).load_app()


def set_env_value(ctx, param, value):
    os.environ["FRASCO_ENV"] = value or "prod"


env_option = click.Option(['-e', '--env'],
    help='The runtime environment',
    callback=set_env_value, is_eager=True)


class FrascoGroup(FlaskGroup):
    def __init__(self, add_default_commands=True, add_env_option=True, **kwargs):
        params = list(kwargs.pop('params', None) or ())
        if add_env_option:
            params.append(env_option)
        super(FrascoGroup, self).__init__(add_default_commands=False, params=params, **kwargs)
        if add_default_commands:
            self.add_command(run_command)
            self.add_command(start_command)
            self.add_command(serve_command)
            self.add_command(shell_command)
            self.add_command(planet_command)
            self.add_command(init_command)
            self.add_command(gen_command)

    def main(self, *args, **kwargs):
        obj = kwargs.get('obj')
        if obj is None:
            obj = FrascoScriptInfo(create_app=self.create_app)
        kwargs['obj'] = obj
        kwargs.setdefault('auto_envvar_prefix', 'FRASCO')
        super(FrascoGroup, self).main(*args, **kwargs)


cli = FrascoGroup(help="""\
This shell command acts as general utility script for Frasco applications.

It will search for an app.yml file in the current directory or use the
one provided using the --app parameter or the FRASCO_APP environment variable.

The most useful command is "run".

Example usage:

  frasco --debug run
""")


def main(as_module=False):
    """This is copy/paste of flask.cli.main to instanciate our own group
    """
    this_module = __package__
    args = sys.argv[1:]

    if as_module:
        if sys.version_info >= (2, 7):
            name = 'python -m ' + this_module.rsplit('.', 1)[0]
        else:
            name = 'python -m ' + this_module

        # This module is always executed as "python -m flask.run" and as such
        # we need to ensure that we restore the actual command line so that
        # the reloader can properly operate.
        sys.argv = ['-m', this_module] + sys.argv[1:]
    else:
        name = None

    cli.main(args=args, prog_name=name)

