from frasco import Feature, Markup, copy_extra_feature_options, command, Blueprint, signal
from frasco.templating import jinja_fragment_extension, FileLoader
from werkzeug.local import LocalProxy
from flask import _request_ctx_stack
from flask.ext.assets import Environment as BaseEnvironment
from easywebassets import Assets as BaseAssets, Bundle, Package
from webassets.script import CommandLineEnvironment
import os
import logging


def _get_current_assets():
    """Returns the current set of assets in the request stack.
    """
    return getattr(_request_ctx_stack.top, 'current_assets', None)


current_assets = LocalProxy(_get_current_assets)


@jinja_fragment_extension("assets", tag_only=True)
def AssetsExtension(*args, **kwargs):
    pkg = _get_current_assets()
    if args:
        if kwargs:
            items = (Bundle(*args, **kwargs),)
        else:
            items = args
        pkg = Package(env=pkg.env, *items)
    return Markup(pkg.html_tags())


class Environment(BaseEnvironment):
    def init_app(self, app):
        self.app = app
        app.jinja_env.add_extension(AssetsExtension)


class Assets(BaseAssets):
    def __init__(self, app=None, env=None, **kwargs):
        if not env:
            env = Environment(**kwargs)
        super(Assets, self).__init__(env=env)
        self.defaults = []
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.env.init_app(app)
        @app.before_request
        def init_current_assets(*args, **kwargs):
            _request_ctx_stack.top.current_assets = Package(env=self, *self.defaults)


class AssetsBlueprint(Blueprint):
    def __init__(self, name, import_name, **kwargs):
        kwargs.setdefault('static_url_path', '/static/vendor/%s' % name)
        kwargs.setdefault('static_folder', 'static')
        super(AssetsBlueprint, self).__init__(name, import_name, **kwargs)


class AssetsFeature(Feature):
    name = "assets"
    ignore_attributes = ["cli_env"]

    before_build_signal = signal('before_assets_build')
    after_build_signal = signal('after_assets_build')
    before_clean_signal = signal('before_assets_clean')
    after_clean_signal = signal('after_assets_clean')
    
    def init_app(self, app):
        copy_extra_feature_options(self, app.config, "ASSETS_")
        if "ASSETS_DEBUG" not in app.config and app.debug:
            app.config["ASSETS_DEBUG"] = True
        self.app = app
        app.assets = self.assets = Assets(app)
        app.jinja_env.loader.bottom_loaders.append(FileLoader(
            os.path.join(os.path.dirname(__file__), "layout.html"), "assets_layout.html"))
        app.jinja_env.loader.set_layout_alias("assets_layout.html")
        app.config.setdefault('EXPORTED_JS_VARS', {})

    def init_declarative(self, app):
        if "ASSETS" in app.config:
            app.assets.register(app.config["ASSETS"])
            if "default" in app.config["ASSETS"]:
                app.assets.defaults.append("@default")

    def expose_package(self, name, import_name):
        self.app.register_blueprint(AssetsBlueprint(name, import_name))

    def add_default(self, *assets):
        insert_at = 0
        if "@default" in self.app.assets.defaults:
            insert_at = self.app.assets.defaults.index("@default")
        for asset in assets:
            self.app.assets.defaults.insert(insert_at, asset)
            insert_at += 1

    @property
    def cli_env(self):
        log = logging.getLogger('webassets')
        log.addHandler(logging.StreamHandler())
        log.setLevel(logging.DEBUG)
        return CommandLineEnvironment(self.assets.env, log)

    @command()
    def build(self):
        self.before_build_signal.send(self)
        self.cli_env.build()
        self.after_build_signal.send(self)

    @command()
    def watch(self):
        self.cli_env.watch()

    @command()
    def clean(self):
        self.before_clean_signal.send(self)
        self.cli_env.clean()
        self.after_clean_signal.send(self)

    @command()
    def check(self):
        self.cli_env.check()