# encoding: utf-8

from static_bundle import StandardBuilder
from static_bundle import BuilderConfig


class FlaskBuilderConfig(BuilderConfig):
    """
    BuilderConfig wrapper
    Working with some Flask app config attributes

    @type app: flask.Flask
    """

    def __init__(self, app):
        self.app = app
        super(FlaskBuilderConfig, self).__init__(input_dir=app.config.get('STATIC_BUNDLE_INPUT_PATH'),
                                                 output_dir=app.config.get('STATIC_BUNDLE_OUTPUT_PATH'),
                                                 env=app.config.get('STATIC_BUNDLE_ENV'),
                                                 url_prefix=app.config.get('STATIC_BUNDLE_URL_PREFIX', '/static/'),
                                                 copy_only_bundles=app.config.get('STATIC_BUNDLE_COPY_ONLY_BUNDLES', False))


class StaticManager(object):
    """
    Extension static manager
    Main class that provides rewrite feature and builds configure

    @type app: flask.Flask
    """

    def __init__(self, app):
        self.app = app
        self.init_rewrite()
        self.init_template_extension()

    def init_rewrite(self):
        app = self.app
        rewrite_path = app.config.get('STATIC_BUNDLE_URL_PREFIX', '/static/')
        if app.config.get('STATIC_BUNDLE_REWRITE', False):
            assert rewrite_path != '' and rewrite_path != '/', "Can't rewrite global paths"
            from flask.helpers import send_from_directory

            if app.config.get('STATIC_BUNDLE_ENV') == 'production':
                app.logger.warning("Static rewrite in production environment. Use collect static instead.")
                static_path = app.config.get('STATIC_BUNDLE_OUTPUT_PATH')
                assert static_path, 'Option OUTPUT_PATH is required for static rewrite in production environment';
            else:
                static_path = app.config.get('STATIC_BUNDLE_INPUT_PATH')
                assert static_path, 'Option INPUT_PATH is required for static rewrite in development environment';
            @app.route(rewrite_path + '<path:filename>')
            def rewrite_static(filename):
                cache_timeout = app.get_send_file_max_age(filename)
                return send_from_directory(BuilderConfig.init_path(static_path), filename,
                                           cache_timeout=cache_timeout)

    def init_template_extension(self):
        self.app.jinja_options['extensions'].append('flask.ext.static_bundle.AssetTemplateExtension')

    @property
    def builder_config(self):
        return FlaskBuilderConfig(self.app)

    def create_builder(self, cls=StandardBuilder):
        return cls(self.builder_config)