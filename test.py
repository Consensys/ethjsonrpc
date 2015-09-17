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

################################################################################
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

################################################################################
print '*' * 80

db_name = 'db_name'
k = 'my_key'
v = 'my_value'
print c.db_putString(db_name, k, v)
x = c.db_getString(db_name, k)
print x
assert v == x

db_name = 'db_name'
k = 'my_key'
v = '0xabcdef'
print c.db_putHex(db_name, k, v)
x = c.db_getHex(db_name, k)
print x
assert v == x

################################################################################
print '*' * 80

b = (199583, '0x19d761c6f944eefe91ad70b9aff3d2d76c972e5bb68c443eea7c0eaa144cef9f')
print c.eth_getBlockByHash(b[1], tx_objects=False)

for x in ['earliest', 'latest', 'pending', b[0]]:
    print c.eth_getBlockByNumber(x, tx_objects=False)

tx = '0x12cd5d9a82049154c8990214a551479853d1bfe45852688833bc4ef86a29b1a3'
print c.eth_getTransactionByHash(tx)

################################################################################
print '*' * 80

code = 'contract Test {}'
print c.eth_compileSolidity(code)

#code = ''
#print c.eth_compileSerpent(code)

#code = ''
#print c.eth_compileLLL(code)

################################################################################
print '*' * 80

b = (246236, '0xcd43703a1ead33ffa1f317636c7b67453c5cc03a3350cd71dbbdd70fcbe0987a')
index = 2
print c.eth_getTransactionByBlockHashAndIndex(b[1], index)

for x in ['earliest', 'latest', 'pending', b[0]]:
    print c.eth_getTransactionByBlockNumberAndIndex(b[0], index)

tx = '0x27191ea9e8228c98bc4418fa60843540937b0c615b2db5e828756800f533f8cd'
print c.eth_getTransactionReceipt(tx)

b = (246294, '0x3d596ca3c7b344419567957b41b2132bb339d365b6b6b3b6a7645e5444914a16')
index = 0
print c.eth_getUncleByBlockHashAndIndex(b[1], index)

for x in ['earliest', 'latest', 'pending', b[0]]:
    print c.eth_getUncleByBlockNumberAndIndex(b[0], index)
