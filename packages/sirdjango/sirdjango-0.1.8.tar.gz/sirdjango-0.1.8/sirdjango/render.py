from __future__ import absolute_import, print_function, unicode_literals


def render_json(data, blocks):
    if not isinstance(data, dict):
        raise ValueError('Invalid block data')

    raw_blocks = data.get('data', None)
    if not isinstance(raw_blocks, list):
        raise ValueError('Invalid block data')

    block_map = dict((b.block_type, b) for b in blocks)
    return ''.join(render_block(raw_block, block_map) for raw_block in data['data'])


def render_block(raw_block, block_map):
    block = block_map[raw_block['type']]
    return block.render_json(raw_block['data'])
