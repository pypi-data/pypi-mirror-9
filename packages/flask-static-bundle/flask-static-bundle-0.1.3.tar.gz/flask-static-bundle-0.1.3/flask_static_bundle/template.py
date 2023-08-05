# encoding: utf-8

from static_bundle import StandardBuilder
from jinja2 import nodes, Markup
from jinja2.ext import Extension


def resolve_builder(builder_name):
    components = builder_name.split('.')
    builder_name = components[-1]
    module_path = components[:-1]
    module = __import__('.'.join(module_path), fromlist=[builder_name])
    return getattr(module, builder_name)


class AssetTemplateExtension(Extension):

    tags = set(['asset'])

    def __init__(self, environment):
        super(AssetTemplateExtension, self).__init__(environment)

    def parse(self, parser):
        stream = parser.stream
        tag = stream.next()
        args = [parser.parse_expression()]
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        return nodes.Output([self.call_method('render_asset', args=args)]).set_lineno(tag.lineno)

    def render_asset(self, builder, asset_name):
        if not isinstance(builder, StandardBuilder):
            builder = resolve_builder(builder)
        return Markup(builder.render_asset(asset_name))

