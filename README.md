# ethjsonrpc

Python client for Ethereum using the JSON-RPC interface

* lightweight
* complete: implements all 60 JSON-RPC methods

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
u'Geth/v1.1.3/linux/go1.5'
>>> c.eth_gasPrice()
50000000000
>>> c.eth_blockNumber()
230891
```

## Additional examples

Please see `test.py` for additional examples.

## See also

* https://github.com/ethereum/wiki/wiki/JSON-RPC
