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

print '*' * 80

addr = '0x1dcb8d1f0fcc8cbc8c2d76528e877f915e299fbe'
for x in ['earliest', 'latest', 'pending', 150000]:
    result = c.eth_getTransactionCount(addr, x)
    print 'eth_getTransactionCount: %s (%s)' % (result, type(result))

b = (231301, '0x9476018748ba1dae5bdf5e3725f8966df1fa127d49f58e66f621bf6868a23c85')
result = c.eth_getBlockTransactionCountByHash(b[1])
print 'eth_getBlockTransactionCountByHash: %s (%s)' % (result, type(result))

for x in ['earliest', 'latest', 'pending', b[0]]:
    result = c.eth_getBlockTransactionCountByNumber(x)
    print 'eth_getBlockTransactionCountByNumber: %s (%s)' % (result, type(result))


b = (199583, '0x19d761c6f944eefe91ad70b9aff3d2d76c972e5bb68c443eea7c0eaa144cef9f')
result = c.eth_getUncleCountByBlockHash(b[1])
print 'eth_getUncleCountByBlockHash: %s (%s)' % (result, type(result))

for x in ['earliest', 'latest', 'pending', b[0]]:
    result = c.eth_getUncleCountByBlockNumber(x)
    print 'eth_getUncleCountByBlockNumber: %s (%s)' % (result, type(result))
