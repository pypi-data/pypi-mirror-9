from __future__ import absolute_import, unicode_literals

from jsonfield import JSONField

from . import fields
from .conf import settings
from .widgets import SirTrevorWidget
from .render import render_json


def default():
    return {'data': []}


class SirTrevorField(JSONField):

    def __init__(self, blocks=None, **kwargs):
        kwargs.setdefault('default', default)
        super(SirTrevorField, self).__init__(**kwargs)
        self.blocks = blocks

    def formfield(self, **kwargs):
        blocks = self.get_blocks()
        options = {
            'blocks': blocks,
            'form_class': fields.SirTrevorField,
            'widget': SirTrevorWidget(blocks=blocks),
        }
        options.update(**kwargs)
        out = super(SirTrevorField, self).formfield(**options)
        return out

    def get_blocks(self):
        blocks = self.blocks
        if blocks is None:
            blocks = settings.get_default_blocks()
        return list(b() if isinstance(b, type) else b for b in blocks)

    def contribute_to_class(self, cls, name):
        super(SirTrevorField, self).contribute_to_class(cls, name)
        render = lambda model: render_json(getattr(model, self.name), self.get_blocks())
        setattr(cls, 'get_{0}_html'.format(self.name), render)

    def deconstruct(self):
        name, path, args, kwargs = super(SirTrevorField, self).deconstruct()
        kwargs['blocks'] = self.blocks
        return name, path, args, kwargs

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^sirdjango\.models\.SirTrevorField"])
except ImportError:
    pass
