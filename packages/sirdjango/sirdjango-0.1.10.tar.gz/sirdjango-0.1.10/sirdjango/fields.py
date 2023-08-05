from __future__ import absolute_import, unicode_literals

import json

from django.core.exceptions import ValidationError
from django.forms import fields
from django.utils.six import text_type

from .conf import settings
from .widgets import SirTrevorWidget


class BlockValidationError(ValidationError):
    def __init__(self, block_path, message):
        super(BlockValidationError, self).__init__(message)
        self.block_path = block_path


class BlockListValidationError(ValidationError):
    def __init__(self, block_errors):
        super(BlockListValidationError, self).__init__('Invalid data')
        self.block_errors = block_errors


class SirTrevorField(fields.Field):
    widget = SirTrevorWidget

    def __init__(self, blocks=None, **kwargs):
        super(SirTrevorField, self).__init__(**kwargs)
        self.blocks = blocks

    def to_python(self, value):
        if isinstance(value, text_type):
            try:
                value = json.loads(value)
            except ValueError:
                raise ValidationError("Invalid JSON data")
        return self.process_data(value)

    def get_blocks(self):
        blocks = self.blocks
        if blocks is None:
            blocks = settings.get_default_blocks()
        return list(b() if isinstance(b, type) else b for b in blocks)

    def process_data(self, data):
        if not isinstance(data, dict) or set(data.keys()) != set(['data']):
            raise ValidationError("Invalid JSON data")

        raw_blocks = data['data']
        if not isinstance(raw_blocks, list):
            raise ValidationError("Invalid JSON data")

        cleaned_blocks = list(self.process_blocks(raw_blocks))
        block_errors = {block['error'].block_path: block['error'].message
                        for block in cleaned_blocks
                        if block['error'] is not None}
        if block_errors:
            self.widget.errors = block_errors
            raise BlockListValidationError(block_errors)

        return {'data': cleaned_blocks}

    def process_blocks(self, raw_blocks):
        block_types = self.get_blocks()
        block_type_map = dict((b.block_type, b) for b in block_types)
        for i, raw_block in enumerate(raw_blocks):
            if raw_block['type'] not in block_type_map:
                yield {
                    'type': raw_block['type'],
                    'data': None,
                    'error': BlockValidationError(i, 'Unknown block type')
                }

            block_type = block_type_map[raw_block['type']]
            raw_block_data = raw_block['data']
            try:
                out = block_type.clean(raw_block_data)
                err = None
            except ValidationError as e:
                out = None
                err = BlockValidationError(i, e.message)
            yield {
                'type': block_type.block_type,
                'data': out,
                'error': err,
            }
