from .constants import BLOCK_TAGS


def hex_to_int(x):
    return int(x, 16)


def validate_block(block):
    if isinstance(block, basestring):
        if block not in BLOCK_TAGS:
            raise ValueError('invalid block tag')
    if isinstance(block, int):
        block = hex(block)
    return block
