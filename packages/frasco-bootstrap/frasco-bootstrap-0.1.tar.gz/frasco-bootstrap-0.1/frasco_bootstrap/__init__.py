from frasco import Feature, hook, current_context
from frasco.templating import FileLoader
from jinja2 import PackageLoader
import os


class BootstrapFeature(Feature):
    name = "bootstrap"
    requires = ["assets"]
    defaults = {"auto_assets": True,
                "with_jquery": True,
                "with_fontawesome": False,
                "fluid_layout": False,
                "bootstrap_version": "3.3.1",
                "jquery_version": "2.1.1",
                "fontawesome_version": "4.2.0"}

    def init_app(self, app):
        path = os.path.dirname(__file__)
        app.jinja_env.macros.register_package(__name__, prefix="bootstrap")
        app.jinja_env.loader.feature_loaders.append(PackageLoader(__name__))
        app.jinja_env.loader.set_layout_alias("bootstrap_layout.html")

        app.assets.register({
            "bootstrap-cdn": [
                "https://maxcdn.bootstrapcdn.com/bootstrap/%s/css/bootstrap.min.css" % self.options['bootstrap_version']],
            "bootstrap-theme-cdn": [
                "https://maxcdn.bootstrapcdn.com/bootstrap/%s/css/bootstrap-theme.min.css" % self.options['bootstrap_version']],
            "bootstrap-js-cdn": [
                "https://maxcdn.bootstrapcdn.com/bootstrap/%s/js/bootstrap.min.js" % self.options['bootstrap_version']],
            "bootstrap-all-cdn": [
                "@bootstrap-cdn",
                "@bootstrap-theme-cdn",
                "@bootstrap-js-cdn"],
            "jquery-cdn": [
                "https://code.jquery.com/jquery-%s.min.js" % self.options['jquery_version']],
            "jquery-bootstrap-all-cdn": [
                "@jquery-cdn",
                "@bootstrap-all-cdn"],
            "font-awesome-cdn": [
                "https://maxcdn.bootstrapcdn.com/font-awesome/%s/css/font-awesome.min.css" % self.options['fontawesome_version']]})

        if self.options["auto_assets"]:
            if self.options["with_fontawesome"]:
                app.features.assets.add_default("@font-awesome-cdn")
            if self.options["with_jquery"]:
                app.features.assets.add_default("@jquery-bootstrap-all-cdn")
            else:
                app.features.assets.add_default("@bootstrap-all-cdn")

    @hook()
    def before_request(self):
        current_context["bs_layout_fluid"] = self.options["fluid_layout"]