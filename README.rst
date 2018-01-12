InfuraEthJsonRpc
==========
Extension of the [ethjsonrpc](https://github.com/ConsenSys/ethjsonrpc)

* Provides classes to query data from an infura node
* To speed up the methods, get an [access token](https://infura.io/register.html) from Infura

Instructions from ethjsonrpc
=============================

Important note
--------------

The API is not yet stable, so please use caution when upgrading.

Installation
------------

You may need additional libraries and tools before installing ethjsonrpc.

On Ubuntu 16.04:

.. code:: bash

   $ sudo apt install python-minimal
   $ sudo apt install gcc
   $ sudo apt install virtualenv  # optional but recommended
   $ sudo apt install libpython-dev
   $ sudo apt install libssl-dev


On Ubuntu 14.04:

.. code:: bash

   $ sudo apt-get install python-virtualenv  # optional but recommended
   $ sudo apt-get install libpython-dev
   $ sudo apt-get install libssl-dev

New Instructions
================
To install:

.. code:: bash

   $ git clone https://github.com/ankitchiplunkar/ethjsonrpc.git
   $ cd ethjsonrpc
   $ python setup.py install


Example
-------

.. code:: python

    >>> c = InfuraEthJsonRpc(network='mainnet')
    # other possible networks are 'ropsten', 'rinkeby', 'kovan' and 'infuranet'
    >>> c.net_version()
    u'1'
    >>> c.web3_clientVersion()
    u'Geth/v1.3.3/linux/go1.5.1'
    >>> c.eth_gasPrice()
    50000000000
    >>> c.eth_blockNumber()
    4896520


Additional examples
-------------------

Please see ``test.py`` for additional examples.

Table of methods
-------------------
Available methods in the three classes:

JSON-RPC	|	InfuraEthJsonRpc	|	EthJsonRpc	|	ParityEthJsonRpc
---	|	---	|	---	|	---
	|		|		|	**trace_filter**
	|		|		|	**trace_get**
	|		|		|	**trace_transaction**
	|		|		|	**trace_block**
	|		|	**call**	|
	|		|	**call_with_transaction**	|
	|		|	**create_contract**	|
	|	**get_contract_address**	|	**get_contract_address**	|
	|		|	**transfer**	|
web3_clientVersion	|	web3_clientVersion	|	web3_clientVersion	|	web3_clientVersion
web3_sha3	|	~~web3_sha3~~	|	web3_sha3	|	web3_sha3
net_version	|	net_version	|	net_version	|	net_version
net_listening	|	net_listening	|	net_listening	|	net_listening
net_peerCount	|	net_peerCount	|	net_peerCount	|	net_peerCount
eth_protocolVersion	|	eth_protocolVersion	|	eth_protocolVersion	|	eth_protocolVersion
eth_syncing	|	eth_syncing	|	eth_syncing	|	eth_syncing
eth_coinbase	|	~~eth_coinbase~~	|	eth_coinbase	|	eth_coinbase
eth_mining	|	eth_mining	|	eth_mining	|	eth_mining
eth_hashrate	|	eth_hashrate	|	eth_hashrate	|	eth_hashrate
eth_gasPrice	|	eth_gasPrice	|	eth_gasPrice	|	eth_gasPrice
eth_accounts	|	eth_accounts	|	eth_accounts	|	eth_accounts
eth_blockNumber	|	eth_blockNumber	|	eth_blockNumber	|	eth_blockNumber
eth_getBalance	|	eth_getBalance	|	eth_getBalance	|	eth_getBalance
eth_getStorageAt	|	eth_getStorageAt	|	eth_getStorageAt	|	eth_getStorageAt
eth_getTransactionCount	|	eth_getTransactionCount	|	eth_getTransactionCount	|	eth_getTransactionCount
eth_getBlockTransactionCountByHash	|	eth_getBlockTransactionCountByHash	|	eth_getBlockTransactionCountByHash	|	eth_getBlockTransactionCountByHash
eth_getBlockTransactionCountByNumber	|	eth_getBlockTransactionCountByNumber	|	eth_getBlockTransactionCountByNumber	|	eth_getBlockTransactionCountByNumber
eth_getUncleCountByBlockHash	|	eth_getUncleCountByBlockHash	|	eth_getUncleCountByBlockHash	|	eth_getUncleCountByBlockHash
eth_getUncleCountByBlockNumber	|	eth_getUncleCountByBlockNumber	|	eth_getUncleCountByBlockNumber	|	eth_getUncleCountByBlockNumber
eth_getCode	|	eth_getCode	|	eth_getCode	|	eth_getCode
eth_sign	|	~~eth_sign~~	|	eth_sign	|	eth_sign
eth_sendTransaction	|	~~eth_sendTransaction~~	|	eth_sendTransaction	|	eth_sendTransaction
eth_sendRawTransaction	|	eth_sendRawTransaction	|	eth_sendRawTransaction	|	eth_sendRawTransaction
eth_call	|	eth_call	|	eth_call	|	eth_call
eth_estimateGas	|	eth_estimateGas	|	eth_estimateGas	|	eth_estimateGas
eth_getBlockByHash	|	eth_getBlockByHash	|	eth_getBlockByHash	|	eth_getBlockByHash
eth_getBlockByNumber	|	eth_getBlockByNumber	|	eth_getBlockByNumber	|	eth_getBlockByNumber
eth_getTransactionByHash	|	eth_getTransactionByHash	|	eth_getTransactionByHash	|	eth_getTransactionByHash
eth_getTransactionByBlockHashAndIndex	|	eth_getTransactionByBlockHashAndIndex	|	eth_getTransactionByBlockHashAndIndex	|	eth_getTransactionByBlockHashAndIndex
eth_getTransactionByBlockNumberAndIndex	|	eth_getTransactionByBlockNumberAndIndex	|	eth_getTransactionByBlockNumberAndIndex	|	eth_getTransactionByBlockNumberAndIndex
eth_getTransactionReceipt	|	eth_getTransactionReceipt	|	eth_getTransactionReceipt	|	eth_getTransactionReceipt
eth_getUncleByBlockHashAndIndex	|	eth_getUncleByBlockHashAndIndex	|	eth_getUncleByBlockHashAndIndex	|	eth_getUncleByBlockHashAndIndex
eth_getUncleByBlockNumberAndIndex	|	eth_getUncleByBlockNumberAndIndex	|	eth_getUncleByBlockNumberAndIndex	|	eth_getUncleByBlockNumberAndIndex
eth_getCompilers	|	eth_getCompilers	|	eth_getCompilers	|	eth_getCompilers
eth_compileSolidity	|	~~eth_compileSolidity~~	|	eth_compileSolidity	|	eth_compileSolidity
eth_compileLLL	|	~~eth_compileLLL~~	|	eth_compileLLL	|	eth_compileLLL
eth_compileSerpent	|	~~eth_compileSerpent~~	|	eth_compileSerpent	|	eth_compileSerpent
eth_newFilter	|	~~eth_newFilter~~	|	eth_newFilter	|	eth_newFilter
eth_newBlockFilter	|	~~eth_newBlockFilter~~	|	eth_newBlockFilter	|	eth_newBlockFilter
eth_newPendingTransactionFilter	|	~~eth_newPendingTransactionFilter~~	|	eth_newPendingTransactionFilter	|	eth_newPendingTransactionFilter
eth_uninstallFilter	|	~~eth_uninstallFilter~~	|	eth_uninstallFilter	|	eth_uninstallFilter
eth_getFilterChanges	|	~~eth_getFilterChanges~~	|	eth_getFilterChanges	|	eth_getFilterChanges
eth_getFilterLogs	|	~~eth_getFilterLogs~~	|	eth_getFilterLogs	|	eth_getFilterLogs
eth_getLogs	|	eth_getLogs	|	eth_getLogs	|	eth_getLogs
eth_getWork	|	eth_getWork	|	eth_getWork	|	eth_getWork
eth_submitWork	|	eth_submitWork	|	eth_submitWork	|	eth_submitWork
eth_submitHashrate	|	eth_submitHashrate	|	eth_submitHashrate	|	eth_submitHashrate
db_putString	|	~~db_putString~~	|	db_putString	|	db_putString
db_getString	|	~~db_getString~~	|	db_getString	|	db_getString
db_putHex	|	~~db_putHex~~	|	db_putHex	|	db_putHex
db_getHex	|	~~db_getHex~~	|	db_getHex	|	db_getHex
shh_version	|	~~shh_version~~	|	shh_version	|	shh_version
shh_post	|	~~shh_post~~	|	shh_post	|	shh_post
shh_newIdentity	|	~~shh_newIdentity~~	|	shh_newIdentity	|	shh_newIdentity
shh_hasIdentity	|	~~shh_hasIdentity~~	|	shh_hasIdentity	|	shh_hasIdentity
shh_newGroup	|	~~shh_newGroup~~	|	shh_newGroup	|	shh_newGroup
shh_addToGroup	|	~~shh_addToGroup~~	|	shh_addToGroup	|	shh_addToGroup
shh_newFilter	|	~~shh_newFilter~~	|	shh_newFilter	|	shh_newFilter
shh_uninstallFilter	|	~~shh_uninstallFilter~~	|	shh_uninstallFilter	|	shh_uninstallFilter
shh_getFilterChanges	|	~~shh_getFilterChanges~~	|	shh_getFilterChanges	|	shh_getFilterChanges
shh_getMessages	|	~~shh_getMessages~~	|	shh_getMessages	|	shh_getMessages

Reference
---------

* https://blog.infura.io/getting-started-with-infura-28e41844cc89
* https://github.com/ethereum/wiki/wiki/JSON-RPC
* https://github.com/ethcore/parity/wiki/JSONRPC-trace-module

