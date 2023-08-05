from __future__ import absolute_import, print_function, unicode_literals

import json

from django.forms import widgets
from django.forms.widgets import flatatt
from django.utils.six import text_type
from django.utils.html import mark_safe, format_html

from .conf import settings


class SirTrevorWidget(widgets.Textarea):

    script_template = '(function() {{' \
                      'var editor = new SirTrevor.Editor({options});' \
                      'var errors = {errors};' \
                      'Object.keys(errors).forEach(function(x) {{' \
                      'editor.blocks[x].addMessage(errors[x], "st-msg--error");' \
                      '}});' \
                      '}})();'
    errors = None

    def __init__(self, blocks=None, extra_options={}, **kwargs):
        super(SirTrevorWidget, self).__init__(**kwargs)
        self.blocks = list(blocks)
        self.block_map = dict((block.block_type, block) for block in blocks)
        self.extra_options = extra_options

    @property
    def media(self):
        media = widgets.Media(**settings.SIRDJANGO_MEDIA)
        for block in self.blocks:
            media += block.media
        return media

    def render(self, name, value, attrs=None):
        if isinstance(value, text_type):
            value = json.loads(value)

        value = {'data': map(self.json_for_editing, value['data'])}
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        final_attrs = self.build_attrs(attrs, name=name)
        textarea = format_html('<textarea{0}>{1}</textarea>',
                               flatatt(final_attrs), value)

        id_ = final_attrs.get('id', None)
        if id_ is None:
            return textarea

        return mark_safe(textarea + self.make_script(id_, self.errors))

    def json_for_editing(self, block_data):
        block_type = block_data['type']
        if block_type not in self.block_map:
            return block_data
        block = self.block_map[block_type]
        return {'type': block_type, 'data': block.json_for_editing(block_data['data'])}

    def make_script(self, id_, errors):
        options = self.get_options('#' + id_)
        script = self.script_template.format(
            options=options,
            errors=json.dumps(errors)
        )
        return '<script>' + script + '</script>'

    def get_options(self, element_selector):
        options = {
            'blockTypes': [block.name for block in self.blocks],
        }
        options.update(self.extra_options)
        # Unforunately, the 'el' option is not valid JSON, but the rest of the
        # options are. Ignore the handcrafted JSON, you saw nothing!
        return '{{el:$({element_selector}), {options}}}'.format(
            element_selector=json.dumps(element_selector),
            options=json.dumps(options)[1:-1])
