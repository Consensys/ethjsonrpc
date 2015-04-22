# Python Ethereum JSON-RPC client #

This module exposes the Ethereum JSON-RPC interface to
Python. Currently supports Serpent contracts.

## Usage ##

### Example contract ###

Example contract: `namecoin.se`

```
# Basic name registry with key ownership

data registry[](owner, value)

def register(key):
    # Key not yet claimed
    if not self.registry[key].owner:
        self.registry[key].owner = msg.sender

def transfer_ownership(key, new_owner):
    if self.registry[key].owner == msg.sender:
        self.registry[key].owner = new_owner

def set_value(key, new_value):
    if self.registry[key].owner == msg.sender:
        self.registry[key].value = new_value

def get_value(key):
    return(self.registry[key].value)

def get_owner(key):
    return(self.registry[key].owner)
```

### Create contract ###

```
import ethjsonrpc
host = '127.0.0.1'
port = 8545
rpc = ethjsonrpc.EthJsonRpc(host, port)

contract_code = open('namecoin.se').read()

contract_address = rpc.create_contract(contract_code)
```

### Interact with contract ###

```
# This loads the function name mappings
rpc.update_code('namecoin.se')

# Send transactions to the blockchain
rpc.eth_sendTransaction(to_address=contract_address, function_name='register', data=['mykey'], value=0)

rpc.eth_sendTransaction(to_address=contract_address, function_name='set_value', data=['mykey', 'myvalue'])

# Do a local function call
myvalue = rpc.eth_call(to_address=contract_address, function_name='get_value', data=['mykey'])
```
