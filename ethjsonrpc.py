import serpent
import requests
import json

from ethereum import utils
from ethereum.abi import ContractTranslator, encode_abi, decode_abi


class EthJsonRpc(object):

    DEFAULT_GAS_FOR_TRANSACTIONS = 500000
    DEFAULT_GAS_PRICE = 10*10**12 #10 szabo

    def __init__(self, host, port, contract_code=None, contract_address=None):

        # If we don't raise the exceptions below, it's kind of hard to identify
        # the problem when any of these variables are null.
        if host is None:
            raise RuntimeError('RPC hostname cannot be null')
        if port is None:
            raise RuntimeError('RPC port cannot be null')

        self.host = host
        self.port = port
        self.contract_code = None
        self.signature = None
        self.translation = None
        self.contract_address = contract_address
        self.update_code(contract_code)
        self.compilers = {}
        try:
            import serpent
            self.compilers['serpent'] = serpent.compile
            self.compilers['lll'] = serpent.compile_lll
        except ImportError:
            print "[WARNING] Could not import module 'serpent'. Compiler will not be available."
        try:
            import solidity
            self.compilers['solidity'] = solidity.compile
        except ImportError:
            try:
                from ethereum._solidity import solc_wrapper
                self.compilers['solidity'] = solc_wrapper.compile
            except ImportError:
                print "[WARNING] Could not import module 'solidity or solc_wrapper'. Compiler will not be available."

    def update_code(self, contract_code):
        if contract_code:
            self.contract_code = contract_code
            self.signature = serpent.mk_full_signature(contract_code)
            self.translation = ContractTranslator(self.signature)

    def _call(self, method, params=None, _id=0):

        params = params or []
        data = json.dumps({
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': _id
        })
        response = requests.post("http://{0}:{1}".format(self.host, self.port), data=data).json()
        if 'result' in response:
            return response['result']
        else:
            raise RuntimeError('Error from RPC call. Returned payload: {0}'.format(response))

    def _encode_function(self, signature, param_values):

        prefix = utils.big_endian_to_int(utils.sha3(signature)[:4])

        if signature.find('(') == -1:
            raise RuntimeError('Invalid function signature. Missing "(" and/or ")"...')

        if signature.find(')') - signature.find('(') == 1:
            return utils.encode_int(prefix)

        types = signature[signature.find('(') + 1: signature.find(')')].split(',')
        encoded_params = encode_abi(types, param_values)
        return utils.zpad(utils.encode_int(prefix), 4) + encoded_params

    def _install_contract(self, language, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        byte_code = self.compilers[language](contract_code)
        return self.eth_sendTransaction(data=byte_code, value=value, from_address=from_address, gas=gas, gas_price=gas_price)
        
    def install_solidity_contract(self, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        """
        Installs a solidity contract into ethereum node
        """
        return self._install_contract('solidity', contract_code, value, from_address, gas, gas_price)
        
    def install_serpent_contract(self, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        """
        Installs a serpent contract into ethereum node
        """
        return self._install_contract('serpent', contract_code, value, from_address, gas, gas_price)

    def install_lll_contract(self, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        """
        Installs a lll contract into ethereum node
        """
        return self._install_contract('lll', contract_code, value, from_address, gas, gas_price)

    def contract_instant_call(self, to_address, function_signature, function_parameters=None, result_types=None, default_block="latest"):
        """
        This method makes a instant call on a contract function without the need to have the contract source code.
        Examples of function_signature in solidity:
            mult(uint x, uint y) => sig: mult(uint256,uint256) (all uint should be transformed to uint256)
            setAddress(address entity_address) =>  sig:setAddress(address)
            doSomething() => sig: doSomething() (functions with no parameters must end with the '()')
        In serpent, all functions parameter signatures are int256. Example:
            setXYZ(x, y, z) => sig: setXYZ(int256,int256,int256)
        """
        data = self._encode_function(function_signature, function_parameters)
        params = [
            {
                'to': to_address,
                'data': '0x{0}'.format(data.encode('hex'))
            },
            default_block
        ]
        response = self._call('eth_call', params)
        return decode_abi(result_types, response[2:].decode('hex'))

    def contract_transaction_call(self, to_address, function_signature, function_parameters=None, from_address=None, gas=None, gas_price=None, default_block="latest"):
        """
        This method makes a call on a contract function through a transaction. Returns the transaction_id.
        Examples of function_signature in solidity:
            mult(uint x, uint y) => sig: mult(uint256,uint256) (all uint should be transformed to uint256)
            setAddress(address entity_address) =>  sig:setAddress(address)
            doSomething() => sig: doSomething() (functions with no parameters must end with the '()')
        In serpent, all functions parameter signatures are int256. Example:
            setXYZ(x, y, z) => sig: setXYZ(int256,int256,int256)
        """
        # Default values for gas and gas_price
        gas = gas or self.DEFAULT_GAS_FOR_TRANSACTIONS
        gas_price = gas_price or self.DEFAULT_GAS_PRICE

        # Default value for from_address
        from_address = from_address or self.eth_accounts()[0]

        data = self._encode_function(function_signature, function_parameters)

        params = {
            'from': from_address,
            'to': to_address,
            'gas': '0x{0:x}'.format(gas),
            'gasPrice': '0x{0:x}'.format(gas_price),
            'value': None,
            'data': '0x{0}'.format(data.encode('hex')) if data else None
        }
        response = self._call('eth_sendTransaction', [params])
        return response

    def create_contract(self, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        self.update_code(contract_code)
        byte_code = serpent.compile(contract_code)

        self.contract_address = self.eth_sendTransaction(data=byte_code, value=value, from_address=from_address, gas=gas, gas_price=gas_price)
        return self.contract_address

    def eth_sendTransaction(self, to_address=None, function_name=None, data=None, value=0, from_address=None, gas=None, gas_price=None):
        """
        Creates new message call transaction or a contract creation, if the data field contains code.
        """
        # Default values for gas and gas_price
        gas = gas or self.DEFAULT_GAS_FOR_TRANSACTIONS
        gas_price = gas_price or self.DEFAULT_GAS_PRICE

        # Default value for from_address
        from_address = from_address or self.eth_accounts()[0]

        if function_name:
            if data is None:
                data = []
            data = self.translation.encode(function_name, data)

        params = {
            'from': from_address,
            'to': to_address,
            'gas': '0x{0:x}'.format(gas),
            'gasPrice': '0x{0:x}'.format(gas_price),
            'value': '0x{0:x}'.format(value) if value else None,
            'data': '0x{0}'.format(data.encode('hex')) if data else None
        }
        return self._call('eth_sendTransaction', [params])

    def web3_clientVersion(self):
        """
        Returns the current client version.
        """
        return self._call('web3_clientVersion')

    def web3_sha3(self, data):
        """
        Returns SHA3 of the given data.
        """
        data = str(data).encode('hex')
        return self._call('web3_sha3', [data])

    def net_version(self):
        """
        Returns the current network protocol version.
        """
        return self._call('net_version')

    def net_peerCount(self):
        """
        Returns number of peers currently connected to the client.
        """
        return self._call('net_peerCount')

    def net_listening(self):
        """
        Returns true if client is actively listening for network connections.
        """
        return self._call('net_listening')

    def eth_version(self):
        """
        Returns the current ethereum protocol version.
        """
        return self._call('eth_version')

    def eth_coinbase(self):
        """
        Returns the client coinbase address.
        """
        return self._call('eth_coinbase')

    def eth_mining(self):
        """
        Returns true if client is actively mining new blocks.
        """
        return self._call('eth_mining')

    def eth_gasPrice(self):
        """
        Returns the current price per gas in wei.
        """
        return self._call('eth_gasPrice')

    def eth_accounts(self):
        """
        Returns a list of addresses owned by client.
        """
        return self._call('eth_accounts')

    def eth_blockNumber(self):
        """
        Returns the number of most recent block.
        """
        return self._call('eth_blockNumber')

    def eth_getBalance(self, address, default_block="latest"):
        """
        Returns the balance of the account of given address.
        """
        return self._call('eth_getBalance', [address, default_block])

    def eth_getStorageAt(self, address, position, default_block="latest"):
        """
        Returns the value from a storage position at a given address.
        """
        return self._call('eth_getStorageAt', [address, hex(position), default_block])

    def eth_getTransactionCount(self, address, default_block="latest"):
        """
        Returns the number of transactions send from a address.
        """
        return self._call('eth_getTransactionCount', [address, default_block])

    def eth_getBlockTransactionCountByHash(self, block_hash):
        """
        Returns the number of transactions in a block from a block matching the given block hash.
        """
        return self._call('eth_getTransactionCount', [block_hash])

    def eth_getBlockTransactionCountByNumber(self, block_number):
        """
        Returns the number of transactions in a block from a block matching the given block number.
        """
        return self._call('eth_getBlockTransactionCountByNumber', [hex(block_number)])

    def eth_getUncleCountByBlockHash(self, block_hash):
        """
        Returns the number of uncles in a block from a block matching the given block hash.
        """
        return self._call('eth_getUncleCountByBlockHash', [block_hash])

    def eth_getUncleCountByBlockNumber(self, block_number):
        """
        Returns the number of uncles in a block from a block matching the given block number.
        """
        return self._call('eth_getUncleCountByBlockNumber', [hex(block_number)])

    def eth_getCode(self, address, default_block="latest"):
        """
        Returns code at a given address.
        """
        return self._call('eth_getCode', [address, default_block])

    def eth_call(self, to_address, function_name, data=None, code=None, default_block="latest"):
        """
        Executes a new message call immediately without creating a transaction on the block chain.
        """
        data = data or []
        data = self.translation.encode(function_name, data)
        params = [
            {
                'to': to_address,
                'data': '0x{0}'.format(data.encode('hex'))
            },
            default_block
        ]
        response = self._call('eth_call', params)
        if function_name:
            response = self.translation.decode(function_name, response[2:].decode('hex'))
        return response

    def eth_getBlockByHash(self, block_hash, transaction_objects=True):
        """
        Returns information about a block by hash.
        """
        return self._call('eth_getBlockByHash', [block_hash, transaction_objects])

    def eth_flush(self):
        """
        """
        return self._call('eth_flush')

    def eth_getBlockByNumber(self, block_number, transaction_objects=True):
        """
        Returns information about a block by hash.
        """
        return self._call('eth_getBlockByNumber', [block_number, transaction_objects])

    def eth_getTransactionByHash(self, transaction_hash):
        """
        Returns the information about a transaction requested by transaction hash.
        """
        return self._call('eth_getTransactionByHash', [transaction_hash])

    def eth_getTransactionByBlockHashAndIndex(self, block_hash, index):
        """
        Returns information about a transaction by block hash and transaction index position.
        """
        return self._call('eth_getTransactionByBlock_hashAndIndex', [block_hash, hex(index)])

    def eth_getTransactionByBlockNumberAndIndex(self, block_number, index):
        """
        Returns information about a transaction by block number and transaction index position.
        """
        return self._call('eth_getTransactionByBlock_numberAndIndex', [block_number, hex(index)])

    def eth_getUncleByBlockHashAndIndex(self, block_hash, index, transaction_objects=True):
        """
        Returns information about a uncle of a block by hash and uncle index position.
        """
        return self._call('eth_getUncleByBlock_hashAndIndex', [block_hash, hex(index), transaction_objects])

    def eth_getUncleByBlockNumberAndIndex(self, block_number, index, transaction_objects=True):
        """
        Returns information about a uncle of a block by number and uncle index position.
        """
        return self._call('eth_getUncleByBlock_numberAndIndex', [block_number, hex(index), transaction_objects])

    def eth_getCompilers(self):
        """
        Returns a list of available compilers in the client.
        """
        return self._call('eth_getCompilers')

    def eth_compileLLL(self, code):
        """
        Returns compiled LLL code.
        """
        return self._call('eth_compileLLL', [code])

    def eth_compileSolidity(self, code):
        """
        Returns compiled solidity code.
        """
        return self._call('eth_compileSolidity', [code])

    def eth_compileSerpent(self, code):
        """
        Returns compiled serpent code.
        """
        return self._call('eth_compileSerpent', [code])

    def eth_newFilter(self, from_block="latest", to_block="latest", address=None, topics=None):
        """
        Creates a filter object, based on filter options, to notify when the state changes (logs).
        To check if the state has changed, call eth_getFilterChanges.
        """
        _filter = {
            'fromBlock': from_block,
            'toBlock': to_block,
            'address': address,
            'topics': topics
        }
        return self._call('eth_newFilter', [_filter])

    def eth_newBlockFilter(self, default_block="latest"):
        """
        Creates a filter object, based on an option string, to notify when state changes (logs). To check if the state has changed, call eth_getFilterChanges.
        """
        return self._call('eth_newBlockFilter', [default_block])

    def eth_uninstallFilter(self, filter_id):
        """
        Uninstalls a filter with given id. Should always be called when watch is no longer needed. Additionally Filters timeout when they aren't requested with eth_getFilterChanges for a period of time.
        """
        return self._call('eth_uninstallFilter', [filter_id])

    def eth_getFilterChanges(self, filter_id):
        """
        Polling method for a filter, which returns an array of logs which occurred since last poll.
        """
        return self._call('eth_getFilterChanges', [filter_id])

    def eth_getFilterLogs(self, filter_id):
        """
        Returns an array of all logs matching filter with given id.
        """
        return self._call('eth_getFilterLogs', [filter_id])

    def eth_getLogs(self, filter_object):
        """
        Returns an array of all logs matching a given filter object.
        """
        return self._call('eth_getLogs', [filter_object])

    def eth_getWork(self):
        """
        Returns the hash of the current block, the seedHash, and the difficulty to be met.
        """
        return self._call('eth_getWork')

    def eth_submitWork(self, nonce, header, mix_digest):
        """
        Used for submitting a proof-of-work solution.
        """
        return self._call('eth_submitWork', [nonce, header, mix_digest])

    def db_putString(self, database_name, key_name, string):
        """
        Stores a string in the local database.
        """
        return self._call('db_putString', [database_name, key_name, string])

    def db_getString(self, database_name, key_name):
        """
        Stores a string in the local database.
        """
        return self._call('db_getString', [database_name, key_name])

    def db_putHex(self, database_name, key_name, string):
        """
        Stores binary data in the local database.
        """
        return self._call('db_putHex', [database_name, key_name, string.encode('hex')])

    def db_getHex(self, database_name, key_name):
        """
        Returns binary data from the local database.
        """
        return self._call('db_getString', [database_name, key_name]).decode('hex')

    def shh_post(self, topics, payload, priority, ttl, _from=None, to=None):
        """
        Sends a whisper message.
        ttl is time-to-live in seconds (integer)
        priority is integer
        """
        whisper_object = {
            'from': _from,
            'to': to,
            'topics': topics,
            'payload': payload,
            'priority': hex(priority),
            'ttl': hex(ttl)
        }
        return self._call('shh_post', [whisper_object])

    def shh_version(self):
        """
        Returns the current whisper protocol version.
        """
        return self._call('shh_version')

    def shh_newIdentity(self):
        """
        Creates new whisper identity in the client.
        """
        return self._call('shh_newIdentity')

    def shh_hasIdentity(self, address):
        """
        Checks if the client hold the private keys for a given identity.
        """
        return self._call('shh_hasIdentity', [address])

    def shh_newGroup(self):
        """
        """
        return self._call('shh_hasIdentity')

    def shh_addToGroup(self):
        """
        """
        return self._call('shh_addToGroup')

    def shh_newFilter(self, to, topics):
        """
        Creates filter to notify, when client receives whisper message matching the filter options.
        """
        _filter = {
            'to': to,
            'topics': topics
        }
        return self._call('shh_newFilter', [_filter])

    def shh_uninstallFilter(self, filter_id):
        """
        Uninstalls a filter with given id. Should always be called when watch is no longer needed.
        Additionally Filters timeout when they aren't requested with shh_getFilterChanges for a period of time.
        """
        return self._call('shh_uninstallFilter', [filter_id])

    def shh_getFilterChanges(self, filter_id):
        """
        Polling method for whisper filters.
        """
        return self._call('shh_getFilterChanges', [filter_id])

    def shh_getMessages(self, filter_id):
        """
        Get all messages matching a filter, which are still existing in the node.
        """
        return self._call('shh_getMessages', [filter_id])
