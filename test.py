from ethjsonrpc import EthJsonRpc

methods = [
    'web3_clientVersion',
    'net_version',
    'net_peerCount',
    'net_listening',
    'eth_protocolVersion',
    'eth_coinbase',
    'eth_mining',
    'eth_hashrate',
    'eth_gasPrice',
    'eth_accounts',
    'eth_blockNumber',
    'eth_getCompilers',
    'eth_newPendingTransactionFilter',
    'eth_getWork',
#    'shh_version',
#    'shh_newIdentity',
#    'shh_newGroup',
]

c = EthJsonRpc()
print len(methods)
for m in methods:
    meth = getattr(c, m)
    result = meth()
    print '%s: %s (%s)' % (m, result, type(result))
