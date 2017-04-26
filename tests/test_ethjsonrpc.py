from ethjsonrpc.client import EthJsonRpc
from ethjsonrpc.utils import hex_to_dec
import sys
import inspect
import pytest
import json
from ethjsonrpc.exceptions import (ConnectionError, BadStatusCodeError,
                                   BadJsonError, BadResponseError)
c = EthJsonRpc()

def isHash ( hash ):
  assert str(hash)[:2] == "0x"

def test_web3_clientVersion ():
  assert len( c.web3_clientVersion() ) > 1

def test_net_version ():
  assert c.net_version() == "1"

def test_net_peerCount ():
  assert c.net_peerCount() == 0

def test_net_listening ():
  assert c.net_listening()

def test_eth_protocolVersion ():
  hex_to_dec(c.eth_protocolVersion()) > 60

def test_eth_syncing ():
  assert not c.eth_syncing()

def test_eth_coinbase ():
  isHash( c.eth_coinbase() )

def test_eth_mining ():
  assert c.eth_mining()

def test_eth_hashrate ():
  assert c.eth_hashrate() >= 0

def test_eth_gasPrice ():
  assert c.eth_gasPrice() >= 0

def test_eth_accounts ():
  l = c.eth_accounts();
  assert isinstance(l,list)
  isHash( l[0] )
  assert len(l) > 0

def test_eth_blockNumber ():
  assert c.eth_blockNumber() > 0

def test_eth_newPendingTransactionFilter ():
  assert c.eth_newPendingTransactionFilter() > 0

def test_eth_getWork ():
  assert isinstance( c.eth_getWork(), list)

@pytest.mark.parametrize("addr,expected", [('0x1dcb8d1f0fcc8cbc8c2d76528e877f915e299fbe',0)] )
@pytest.mark.parametrize("tag", ['earliest', 'latest', 'pending'] )
def test_eth_getTransactionCount(addr, tag, expected):
  assert c.eth_getTransactionCount( addr, tag ) == expected

@pytest.mark.parametrize("addr,expected", [('0x1dcb8d1f0fcc8cbc8c2d76528e877f915e299fbe',0)] )
@pytest.mark.parametrize("quantity", [150000] )
def test_eth_getTransactionCount(addr, quantity, expected):
  assert c.eth_getTransactionCount( addr, quantity ) == expected

@pytest.mark.parametrize("data,expected", [
  ('0x9476018748ba1dae5bdf5e3725f8966df1fa127d49f58e66f621bf6868a23c85',0)])
def test_eth_getBlockTransactionCountByHash(data,expected):
  assert c.eth_getBlockTransactionCountByHash( data ) == expected

@pytest.mark.parametrize("tag,expected", [(231301,0),
  ("earliest",0),("latest",0),("pending",0)])
def test_eth_getBlockTransactionCountByNumber(tag,expected):
  assert c.eth_getBlockTransactionCountByNumber(tag) == expected

@pytest.mark.parametrize("hash", ['0x19d761c6f944eefe91ad70b9aff3d2d76c972e5bb68c443eea7c0eaa144cef9f'])
def test_eth_getUncleCountByBlockHash (hash):
  assert c.eth_getUncleCountByBlockHash(hash) == 0

@pytest.mark.parametrize("tag",['earliest', 'latest', 'pending', 199583])
def test_eth_getUncleCountByBlockNumber (tag):
  assert c.eth_getUncleCountByBlockNumber(tag) == 0

@pytest.mark.parametrize("hash",['0x19d761c6f944eefe91ad70b9aff3d2d76c972e5bb68c443eea7c0eaa144cef9f'])
def test_eth_getBlockByHash (hash):
  assert c.eth_getBlockByHash(hash, tx_objects=False) == None

@pytest.mark.parametrize("tag",['earliest', 'latest'])
def test_eth_getBlockByNumber (tag):
  isHash( c.eth_getBlockByNumber(tag, tx_objects=False)["hash"])

@pytest.mark.parametrize("tx",['0x12cd5d9a82049154c8990214a551479853d1bfe45852688833bc4ef86a29b1a3'])
def test_eth_getTransactionByHash (tx):
  assert c.eth_getTransactionByHash(tx) == None

@pytest.mark.parametrize("hash,index",[('0xcd43703a1ead33ffa1f317636c7b67453c5cc03a3350cd71dbbdd70fcbe0987a',2)])
def test_eth_getTransactionByBlockHashAndIndex (hash,index):
  assert c.eth_getTransactionByBlockHashAndIndex(hash, index) == None

@pytest.mark.parametrize("tag",[246236,'earliest', 'latest', 'pending'])
@pytest.mark.parametrize("index",[2])
def test_eth_getTransactionByBlockNumberAndIndex (tag,index):
  assert c.eth_getTransactionByBlockNumberAndIndex(tag, index) == None

@pytest.mark.parametrize("tx",['0x27191ea9e8228c98bc4418fa60843540937b0c615b2db5e828756800f533f8cd'])
def test_eth_getTransactionReceipt (tx) :
  assert c.eth_getTransactionReceipt(tx) == None

@pytest.mark.parametrize("tag",['0x3d596ca3c7b344419567957b41b2132bb339d365b6b6b3b6a7645e5444914a16'])
@pytest.mark.parametrize("index",[0])
def test_eth_getUncleByBlockHashAndIndex(tag,index):
  assert c.eth_getUncleByBlockHashAndIndex(tag, index) == None

@pytest.mark.parametrize("tag",['earliest', 'latest', 'pending', 246294])
@pytest.mark.parametrize("index",[0])
def test_eth_getUncleByBlockNumberAndIndex(tag,index):
  assert c.eth_getUncleByBlockNumberAndIndex(tag, index) == None

@pytest.mark.parametrize("addr",['0x1dcb8d1f0fcc8cbc8c2d76528e877f915e299fbe'])
@pytest.mark.parametrize("tag",['earliest', 'latest', 'pending', 150000])
def test_eth_getBalance (addr,tag):
  assert c.eth_getBalance(addr, tag) == 0


@pytest.mark.parametrize("addr",["0x407d73d8a49eeb85d32cf465507dd71d507100c1"])
@pytest.mark.parametrize("pos",[0])
@pytest.mark.parametrize("tag", ["earliest","latest","pending",2])
def test_eth_getStorageAt(addr,pos,tag):
  assert hex_to_dec( c.eth_getStorageAt(addr, pos, tag )) == 0

@pytest.mark.parametrize("rate,client",[(1000000,
  "0x59daa26581d0acd1fce254fb7e85952f4c09d0915afd33d3886cd914bc7d283c")])
def test_eth_submitHashrate(rate,client):
  print c.eth_submitHashrate(rate, client)

def test_web3_sha3():
  # keccak-256, not sha3-256
  assert  c.web3_sha3('') == '0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'

def test_create_contract ():
  with pytest.raises(BadResponseError) as err:
    hash = c.create_contract(None, '0x%s' % open('tests/Example.bin', 'r').read(), None )
    # in case "Intrinsic gas too low" wasn't an issue, check return hash
    isHash( hash )
    #request was good, but we still need to throw
    raise BadResponseError()

