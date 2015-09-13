import json
import warnings

import serpent
import requests
from ethereum import utils
from ethereum.abi import ContractTranslator, encode_abi, decode_abi

GETH_DEFAULT_RPC_PORT     = 8545
ETH_DEFAULT_RPC_PORT      = 8080
PYETHAPP_DEFAULT_RPC_PORT = 4000

BLOCK_TAG_EARLIEST = 'earliest'
BLOCK_TAG_LATEST   = 'latest'
BLOCK_TAG_PENDING  = 'pending'
BLOCK_TAGS = (
    BLOCK_TAG_EARLIEST,
    BLOCK_TAG_LATEST,
    BLOCK_TAG_PENDING,
)


class EthJsonRpc(object):

    DEFAULT_GAS_FOR_TRANSACTIONS = 500000
    DEFAULT_GAS_PRICE = 10*10**12 #10 szabo

    def __init__(self, host='localhost', port=GETH_DEFAULT_RPC_PORT, tls=False,
                 contract_code=None, contract_address=None):
        self.host = host
        self.port = port
        self.tls = tls
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
            print '[WARNING] Could not import module "serpent". Compiler will not be available.'
        try:
            import solidity
            self.compilers['solidity'] = solidity.compile
        except ImportError:
            try:
                from ethereum._solidity import solc_wrapper
                self.compilers['solidity'] = solc_wrapper.compile
            except ImportError:
                print '[WARNING] Could not import module "solidity" or "solc_wrapper". Compiler will not be available.'

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
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}'.format(scheme, self.host, self.port)
        response = requests.post(url, data=data).json()
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
        '''
        Installs a solidity contract into ethereum node
        '''
        return self._install_contract('solidity', contract_code, value, from_address, gas, gas_price)
        
    def install_serpent_contract(self, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        '''
        Installs a serpent contract into ethereum node
        '''
        return self._install_contract('serpent', contract_code, value, from_address, gas, gas_price)

    def install_lll_contract(self, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        '''
        Installs a lll contract into ethereum node
        '''
        return self._install_contract('lll', contract_code, value, from_address, gas, gas_price)

    def contract_instant_call(self, to_address, function_signature, function_parameters=None, result_types=None, default_block=BLOCK_TAG_LATEST):
        '''
        This method makes a instant call on a contract function without the need to have the contract source code.
        Examples of function_signature in solidity:
            mult(uint x, uint y) => sig: mult(uint256,uint256) (all uint should be transformed to uint256)
            setAddress(address entity_address) =>  sig:setAddress(address)
            doSomething() => sig: doSomething() (functions with no parameters must end with the '()')
        In serpent, all functions parameter signatures are int256. Example:
            setXYZ(x, y, z) => sig: setXYZ(int256,int256,int256)
        '''
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

    def contract_transaction_call(self, to_address, function_signature, function_parameters=None, from_address=None, gas=None, gas_price=None, default_block=BLOCK_TAG_LATEST):
        '''
        This method makes a call on a contract function through a transaction. Returns the transaction_id.
        Examples of function_signature in solidity:
            mult(uint x, uint y) => sig: mult(uint256,uint256) (all uint should be transformed to uint256)
            setAddress(address entity_address) =>  sig:setAddress(address)
            doSomething() => sig: doSomething() (functions with no parameters must end with the '()')
        In serpent, all functions parameter signatures are int256. Example:
            setXYZ(x, y, z) => sig: setXYZ(int256,int256,int256)
        '''
        # Default values for gas and gas_price
        gas = gas or self.DEFAULT_GAS_FOR_TRANSACTIONS
        gas_price = gas_price or self.DEFAULT_GAS_PRICE

        # Default value for from_address
        from_address = from_address or self.eth_accounts()[0]

        data = self._encode_function(function_signature, function_parameters)

        params = {
            'from':     from_address,
            'to':       to_address,
            'gas':      '0x{0:x}'.format(gas),
            'gasPrice': '0x{0:x}'.format(gas_price),
            'value':    None,
            'data':     '0x{0}'.format(data.encode('hex')) if data else None
        }
        response = self._call('eth_sendTransaction', [params])
        return response

    def create_contract(self, contract_code, value=0, from_address=None, gas=None, gas_price=None):
        self.update_code(contract_code)
        byte_code = serpent.compile(contract_code)

        self.contract_address = self.eth_sendTransaction(data=byte_code, value=value, from_address=from_address, gas=gas, gas_price=gas_price)
        return self.contract_address

################################################################################

    def web3_clientVersion(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#web3_clientversion
        '''
        return self._call('web3_clientVersion')

    def web3_sha3(self, data):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#web3_sha3
        '''
        data = str(data).encode('hex')
        return self._call('web3_sha3', [data])

    def net_version(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version
        '''
        return self._call('net_version')

    def net_peerCount(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_peercount
        '''
        return self._call('net_peerCount')

    def net_listening(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_listening
        '''
        return self._call('net_listening')

    def eth_protocolVersion(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_protocolversion
        '''
        return self._call('eth_protocolVersion')

    def eth_coinbase(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_coinbase
        '''
        return self._call('eth_coinbase')

    def eth_mining(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_mining
        '''
        return self._call('eth_mining')

    def eth_hashrate(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_hashrate
        '''
        return self._call('eth_hashrate')

    def eth_gasPrice(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gasprice
        '''
        return self._call('eth_gasPrice')

    def eth_accounts(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_accounts
        '''
        return self._call('eth_accounts')

    def eth_blockNumber(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_blocknumber
        '''
        return self._call('eth_blockNumber')

    def eth_getBalance(self, address=None, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getbalance
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        address = address or self.eth_coinbase()
        return self._call('eth_getBalance', [address, default_block])

    def eth_getStorageAt(self, address, position, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getstorageat
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        return self._call('eth_getStorageAt', [address, hex(position), default_block])

    def eth_getTransactionCount(self, address, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactioncount
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        return self._call('eth_getTransactionCount', [address, default_block])

    def eth_getBlockTransactionCountByHash(self, block_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblocktransactioncountbyhash
        '''
        return self._call('eth_getBlockTransactionCountByHash', [block_hash])

    def eth_getBlockTransactionCountByNumber(self, block_number):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblocktransactioncountbynumber
        '''
        return self._call('eth_getBlockTransactionCountByNumber', [hex(block_number)])

    def eth_getUncleCountByBlockHash(self, block_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclecountbyblockhash
        '''
        return self._call('eth_getUncleCountByBlockHash', [block_hash])

    def eth_getUncleCountByBlockNumber(self, block_number):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclecountbyblocknumber
        '''
        return self._call('eth_getUncleCountByBlockNumber', [hex(block_number)])

    def eth_getCode(self, address, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcode
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        return self._call('eth_getCode', [address, default_block])

    def eth_sign(self, address, data):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sign
        '''
        return self._call('eth_sign', [address, data])

    def eth_sendTransaction(self, to_address=None, function_name=None, data=None, value=0, from_address=None, gas=None, gas_price=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendtransaction
        '''
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
            'from':     from_address,
            'to':       to_address,
            'gas':      '0x{0:x}'.format(gas),
            'gasPrice': '0x{0:x}'.format(gas_price),
            'value':    '0x{0:x}'.format(value) if value else None,
            'data':     '0x{0}'.format(data.encode('hex')) if data else None
        }
        return self._call('eth_sendTransaction', [params])

    def eth_call(self, to_address, function_name, data=None, code=None, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_call
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
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

    def eth_estimateGas(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_estimategas
        '''
        return self._call('eth_estimateGas')

    def eth_getBlockByHash(self, block_hash, transaction_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbyhash
        '''
        return self._call('eth_getBlockByHash', [block_hash, transaction_objects])

    def eth_getBlockByNumber(self, block_number, transaction_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbynumber
        '''
        return self._call('eth_getBlockByNumber', [block_number, transaction_objects])

    def eth_getTransactionByHash(self, transaction_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyhash
        '''
        return self._call('eth_getTransactionByHash', [transaction_hash])

    def eth_getTransactionByBlockHashAndIndex(self, block_hash, index):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblockhashandindex
        '''
        return self._call('eth_getTransactionByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getTransactionByBlockNumberAndIndex(self, block_number, index):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblocknumberandindex
        '''
        return self._call('eth_getTransactionByBlockNumberAndIndex', [block_number, hex(index)])

    def eth_getTransactionReceipt(self, tx_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionreceipt
        '''
        return self._call('eth_getTransactionReceipt', [tx_hash])

    def eth_getUncleByBlockHashAndIndex(self, block_hash, index, transaction_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblockhashandindex
        '''
        return self._call('eth_getUncleByBlockHashAndIndex', [block_hash, hex(index), transaction_objects])

    def eth_getUncleByBlockNumberAndIndex(self, block_number, index, transaction_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblocknumberandindex
        '''
        return self._call('eth_getUncleByBlockNumberAndIndex', [block_number, hex(index), transaction_objects])

    def eth_getCompilers(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcompilers
        '''
        return self._call('eth_getCompilers')

    def eth_compileLLL(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilelll
        '''
        return self._call('eth_compileLLL', [code])

    def eth_compileSolidity(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilesolidity
        '''
        return self._call('eth_compileSolidity', [code])

    def eth_compileSerpent(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compileserpent
        '''
        return self._call('eth_compileSerpent', [code])

    def eth_newFilter(self, from_block=BLOCK_TAG_LATEST, to_block=BLOCK_TAG_LATEST, address=None, topics=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newfilter
        '''
        _filter = {
            'fromBlock': from_block,
            'toBlock':   to_block,
            'address':   address,
            'topics':    topics,
        }
        return self._call('eth_newFilter', [_filter])

    def eth_newBlockFilter(self, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newblockfilter
        '''
        return self._call('eth_newBlockFilter', [default_block])

    def eth_newPendingTransactionFilter(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newpendingtransactionfilter
        '''
        return self._call('eth_newPendingTransactionFilter')

    def eth_uninstallFilter(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_uninstallfilter
        '''
        return self._call('eth_uninstallFilter', [filter_id])

    def eth_getFilterChanges(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterchanges
        '''
        return self._call('eth_getFilterChanges', [filter_id])

    def eth_getFilterLogs(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs
        '''
        return self._call('eth_getFilterLogs', [filter_id])

    def eth_getLogs(self, filter_object):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getlogs
        '''
        return self._call('eth_getLogs', [filter_object])

    def eth_getWork(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getwork
        '''
        return self._call('eth_getWork')

    def eth_submitWork(self, nonce, header, mix_digest):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submitwork
        '''
        return self._call('eth_submitWork', [nonce, header, mix_digest])

    def eth_submitHashrate(self, hash_rate, client_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submithashrate
        '''
        return self._call('eth_submitHashrate', [hash_rate, client_id])

    def db_putString(self, database_name, key_name, string):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_putstring
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_putString', [database_name, key_name, string])

    def db_getString(self, database_name, key_name):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_getstring
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_getString', [database_name, key_name])

    def db_putHex(self, database_name, key_name, string):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_puthex
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_putHex', [database_name, key_name, string.encode('hex')])

    def db_getHex(self, database_name, key_name):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_gethex
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_getHex', [database_name, key_name]).decode('hex')

    def shh_post(self, topics, payload, priority, ttl, _from=None, to=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_post
        '''
        whisper_object = {
            'from':     _from,
            'to':       to,
            'topics':   topics,
            'payload':  payload,
            'priority': hex(priority),
            'ttl':      hex(ttl)
        }
        return self._call('shh_post', [whisper_object])

    def shh_version(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_version
        '''
        return self._call('shh_version')

    def shh_newIdentity(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newidentity
        '''
        return self._call('shh_newIdentity')

    def shh_hasIdentity(self, address):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_hasidentity
        '''
        return self._call('shh_hasIdentity', [address])

    def shh_newGroup(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newgroup
        '''
        return self._call('shh_newGroup')

    def shh_addToGroup(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_addtogroup
        '''
        return self._call('shh_addToGroup')

    def shh_newFilter(self, to, topics):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newfilter
        '''
        _filter = {
            'to':     to,
            'topics': topics,
        }
        return self._call('shh_newFilter', [_filter])

    def shh_uninstallFilter(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_uninstallfilter
        '''
        return self._call('shh_uninstallFilter', [filter_id])

    def shh_getFilterChanges(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getfilterchanges
        '''
        return self._call('shh_getFilterChanges', [filter_id])

    def shh_getMessages(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getmessages
        '''
        return self._call('shh_getMessages', [filter_id])
