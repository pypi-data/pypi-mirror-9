"""
Flask support for XStatic assets
"""

from flask import send_from_directory
from xstatic.main import XStatic


class FlaskXStatic(object):
    """
    Flask support for XStatic assets.

    You can either provide a Flask app object to the constructor, or initialize
    the application later with init_app.
    """

    def __init__(self, app=None):
        self.app = app
        self.serve_files = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Set up the application so that it can use XStatic assets.

        This creates a route named "xstatic" that expose the static files of
        xstatic modules. For example, the minified version of jquery may be
        accessed using:

        url_for('xstatic', xs_package='jquery', filename='jquery.min.js')
        """
        @app.route('/xstatic/<xs_package>/<path:filename>')
        def xstatic(xs_package, filename):
            """
            Serve static files from Flask-XStatic.
            """
            base_dir = self.serve_files[xs_package]
            return send_from_directory(base_dir, filename)

    def add_module(self, module_name):
        """
        Register a new XStatic module.

        For example, if you want to use jquery, call xs.add_module('jquery').
        Note that in that case, you need to have "xstatic-jquery" installed.
        """
        pkg = __import__('xstatic.pkg', fromlist=[module_name])
        module = getattr(pkg, module_name)
        xs = XStatic(module,
                     root_url='/xstatic',
                     provider='local',
                     protocol='http',
                     )
        self.serve_files[xs.name] = xs.base_dir

    def path_for(self, module_name):
        """
        Compute the base path for a XStatic module, if you want to use it for
        something other than asset serving (for example, if you want to use .js
        or .scss files as sources for webassets).
        """
        return self.serve_files[module_name]
