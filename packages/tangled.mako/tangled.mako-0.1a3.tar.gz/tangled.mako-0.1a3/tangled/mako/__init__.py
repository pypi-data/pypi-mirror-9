import os

from mako.lookup import TemplateLookup as BaseTemplateLookup

from tangled.converters import as_list_of
from tangled.decorators import cached_property
from tangled.settings import parse_settings
from tangled.util import abs_path, asset_path
from tangled.web.events import ApplicationCreated
from tangled.web.representations import HTMLRepresentation, TemplateMixin


def include(app):
    app.add_subscriber(ApplicationCreated, app_created_subscriber)
    app.register_representation_type(
        'tangled.mako:MakoRepresentation', replace=True)
    app.add_representation_arg('text/html', 'template')


def app_created_subscriber(event):
    app = event.app
    lookup = create_lookup(app.settings)
    app['mako.lookup'] = lookup


def create_lookup(settings):
    """Create Mako template lookup after application is created."""
    conversion_map = {
        'default_filters': 'list',
        'directories': as_list_of(abs_path),
        'file_system_checks': 'bool',
        'imports': 'list',
    }
    defaults = {
        'default_filters': 'h',
        'input_encoding': 'utf-8',
        'output_encoding': None,
    }
    lookup_args = parse_settings(
        settings, conversion_map=conversion_map, defaults=defaults,
        prefix='mako.lookup.')
    lookup = TemplateLookup(**lookup_args)
    return lookup


class TemplateLookup(BaseTemplateLookup):

    def get_template(self, uri):
        """Allow absolute and asset paths."""
        if os.path.isabs(uri):
            srcfile = uri
        elif ':' in uri:
            srcfile = asset_path(uri)
        else:
            srcfile = None
        if srcfile and os.path.isabs(srcfile):
            try:
                if self.filesystem_checks:
                    return self._check(uri, self._collection[uri])
                else:
                    return self._collection[uri]
            except KeyError:
                if os.path.isfile(srcfile):
                    return self._load(srcfile, uri)
        return super().get_template(uri)


class MakoRepresentation(TemplateMixin, HTMLRepresentation):

    key = 'mako'

    def __init__(self, *args, template, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = template

    @cached_property
    def lookup(self):
        return self.app['mako.lookup']

    @cached_property
    def template(self):
        return self.lookup.get_template(self.template_name)

    @cached_property
    def content(self):
        return self.template.render(**self.template_context())
