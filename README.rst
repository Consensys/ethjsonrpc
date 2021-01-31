InfuraEthJsonRpc
==========
Extension of the ethjsonrpc library (https://github.com/ConsenSys/ethjsonrpc)

* Provides classes to query data from an infura node
* To speed up the methods, get an access token from Infura. (https://infura.io/register.html)

Earlier instructions 
====================

Important note
--------------

The API is not yet stable, so please use caution when upgrading.

Installation
------------

You may need additional libraries and tools before installing ethjsonrpc.

On Ubuntu 20.04:

.. code:: bash

   $ sudo apt install python2-minimal
   $ sudo apt install gcc
   $ sudo apt install virtualenv  # optional but recommended
   $ sudo apt install libpython2-dev
   $ sudo apt install libssl-dev

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

Table of unavailable methods
-------------------
Since this is not a local node, the following methods are unavailable.

* 	~~web3_sha3~~
* 	~~eth_coinbase~~
* 	~~eth_sign~~
* 	~~eth_sendTransaction~~
* 	~~eth_compileSolidity~~
* 	~~eth_compileLLL~~
*	~~eth_compileSerpent~~
* 	~~eth_newFilter~~
* 	~~eth_newBlockFilter~~
* 	~~eth_newPendingTransactionFilter~~
* 	~~eth_uninstallFilter~~
* 	~~eth_getFilterChanges~~
* 	~~eth_getFilterLogs~~
* 	~~db_putString~~
* 	~~db_getString~~
* 	~~db_putHex~~
* 	~~db_getHex~~
* 	~~shh_version~~
* 	~~shh_post~~
* 	~~shh_newIdentity~~
* 	~~shh_hasIdentity~~
* 	~~shh_newGroup~~
* 	~~shh_addToGroup~~
* 	~~shh_newFilter~~
* 	~~shh_uninstallFilter~~
* 	~~shh_getFilterChanges~~
* 	~~shh_getMessages~~

Reference
---------

* https://blog.infura.io/getting-started-with-infura-28e41844cc89
* https://github.com/ethereum/wiki/wiki/JSON-RPC
* https://github.com/ethcore/parity/wiki/JSONRPC-trace-module

