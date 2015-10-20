from ethjsonrpc.constants import BLOCK_TAGS


def hex_to_dec(x):
    return int(x, 16)


def validate_block(block):
    if isinstance(block, basestring):
        if block not in BLOCK_TAGS:
            raise ValueError('invalid block tag')
    if isinstance(block, int):
        block = hex(block)
    return block


def wei_to_ether(wei):
    return 1.0 * wei / 10**18


def ether_to_wei(ether):
    return ether * 10**18
