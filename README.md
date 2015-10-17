# ethjsonrpc

Python client for Ethereum using the JSON-RPC interface

* lightweight
* complete: implements all 61 JSON-RPC methods

## Important note

The API is not yet stable, so please use caution when upgrading.

## Installation

```bash
$ pip install ethjsonrpc
```

## Example

```python
>>> from ethjsonrpc import EthJsonRpc
>>> c = EthJsonRpc('127.0.0.1', 8545)
>>> c.net_version()
u'1'
>>> c.web3_clientVersion()
u'Geth/v1.2.2/linux/go1.5'
>>> c.eth_gasPrice()
50000000000
>>> c.eth_blockNumber()
386199
```

## Additional examples

Please see `test.py` for additional examples.

## See also

* https://github.com/ethereum/wiki/wiki/JSON-RPC
