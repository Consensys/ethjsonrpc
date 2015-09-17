import json
import warnings

import serpent
import requests
from ethereum import utils
from ethereum.abi import ContractTranslator, encode_abi, decode_abi

from .constants import BLOCK_TAGS, BLOCK_TAG_LATEST
from .utils import hex_to_int, validate_block

GETH_DEFAULT_RPC_PORT     = 8545
ETH_DEFAULT_RPC_PORT      = 8080
PYETHAPP_DEFAULT_RPC_PORT = 4000


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

        TESTED
        '''
        return self._call('web3_clientVersion')

    def web3_sha3(self, data):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#web3_sha3

        NEEDS TESTING
        '''
        data = str(data).encode('hex')
        return self._call('web3_sha3', [data])

    def net_version(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version

        TESTED
        '''
        return self._call('net_version')

    def net_peerCount(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_peercount

        TESTED
        '''
        return hex_to_int(self._call('net_peerCount'))

    def net_listening(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#net_listening

        TESTED
        '''
        return self._call('net_listening')

    def eth_protocolVersion(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_protocolversion

        TESTED
        '''
        return self._call('eth_protocolVersion')

    def eth_coinbase(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_coinbase

        TESTED
        '''
        return self._call('eth_coinbase')

    def eth_mining(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_mining

        TESTED
        '''
        return self._call('eth_mining')

    def eth_hashrate(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_hashrate

        TESTED
        '''
        return hex_to_int(self._call('eth_hashrate'))

    def eth_gasPrice(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gasprice

        TESTED
        '''
        return hex_to_int(self._call('eth_gasPrice'))

    def eth_accounts(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_accounts

        TESTED
        '''
        return self._call('eth_accounts')

    def eth_blockNumber(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_blocknumber

        TESTED
        '''
        return hex_to_int(self._call('eth_blockNumber'))

    def eth_getBalance(self, address=None, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getbalance

        TESTED
        '''
        address = address or self.eth_coinbase()
        block = validate_block(block)
        return hex_to_int(self._call('eth_getBalance', [address, block]))

    def eth_getStorageAt(self, address=None, position=0, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getstorageat

        TESTED
        '''
        block = validate_block(block)
        return self._call('eth_getStorageAt', [address, hex(position), block])

    def eth_getTransactionCount(self, address, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactioncount

        TESTED
        '''
        block = validate_block(block)
        return hex_to_int(self._call('eth_getTransactionCount', [address, block]))

    def eth_getBlockTransactionCountByHash(self, block_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblocktransactioncountbyhash

        TESTED
        '''
        return hex_to_int(self._call('eth_getBlockTransactionCountByHash', [block_hash]))

    def eth_getBlockTransactionCountByNumber(self, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblocktransactioncountbynumber

        TESTED
        '''
        block = validate_block(block)
        return hex_to_int(self._call('eth_getBlockTransactionCountByNumber', [block]))

    def eth_getUncleCountByBlockHash(self, block_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclecountbyblockhash

        TESTED
        '''
        return hex_to_int(self._call('eth_getUncleCountByBlockHash', [block_hash]))

    def eth_getUncleCountByBlockNumber(self, block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclecountbyblocknumber

        TESTED
        '''
        block = validate_block(block)
        return hex_to_int(self._call('eth_getUncleCountByBlockNumber', [block]))

    def eth_getCode(self, address, default_block=BLOCK_TAG_LATEST):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcode

        NEEDS TESTING
        '''
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        return self._call('eth_getCode', [address, default_block])

    def eth_sign(self, address, data):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sign

        NEEDS TESTING
        '''
        return self._call('eth_sign', [address, data])

    def eth_sendTransaction(self, to_address=None, function_name=None, data=None, value=0, from_address=None, gas=None, gas_price=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendtransaction

        NEEDS TESTING
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

        NEEDS TESTING
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

        NEEDS TESTING
        '''
        return self._call('eth_estimateGas')

    def eth_getBlockByHash(self, block_hash, tx_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbyhash

        TESTED
        '''
        return self._call('eth_getBlockByHash', [block_hash, tx_objects])

    def eth_getBlockByNumber(self, block=BLOCK_TAG_LATEST, tx_objects=True):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbynumber

        TESTED
        '''
        block = validate_block(block)
        return self._call('eth_getBlockByNumber', [block, tx_objects])

    def eth_getTransactionByHash(self, tx_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyhash

        TESTED
        '''
        return self._call('eth_getTransactionByHash', [tx_hash])

    def eth_getTransactionByBlockHashAndIndex(self, block_hash, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblockhashandindex

        TESTED
        '''
        return self._call('eth_getTransactionByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getTransactionByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblocknumberandindex

        TESTED
        '''
        block = validate_block(block)
        return self._call('eth_getTransactionByBlockNumberAndIndex', [block, hex(index)])

    def eth_getTransactionReceipt(self, tx_hash):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionreceipt

        TESTED
        '''
        return self._call('eth_getTransactionReceipt', [tx_hash])

    def eth_getUncleByBlockHashAndIndex(self, block_hash, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblockhashandindex

        TESTED
        '''
        return self._call('eth_getUncleByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getUncleByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblocknumberandindex

        TESTED
        '''
        block = validate_block(block)
        return self._call('eth_getUncleByBlockNumberAndIndex', [block, hex(index)])

    def eth_getCompilers(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcompilers

        TESTED
        '''
        return self._call('eth_getCompilers')

    def eth_compileLLL(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilelll

        N/A
        '''
        return self._call('eth_compileLLL', [code])

    def eth_compileSolidity(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilesolidity

        TESTED
        '''
        return self._call('eth_compileSolidity', [code])

    def eth_compileSerpent(self, code):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compileserpent

        N/A
        '''
        return self._call('eth_compileSerpent', [code])

    def eth_newFilter(self, from_block=BLOCK_TAG_LATEST, to_block=BLOCK_TAG_LATEST, address=None, topics=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newfilter

        NEEDS TESTING
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

        NEEDS TESTING
        '''
        return self._call('eth_newBlockFilter', [default_block])

    def eth_newPendingTransactionFilter(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newpendingtransactionfilter

        TESTED
        '''
        return hex_to_int(self._call('eth_newPendingTransactionFilter'))

    def eth_uninstallFilter(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_uninstallfilter

        NEEDS TESTING
        '''
        return self._call('eth_uninstallFilter', [filter_id])

    def eth_getFilterChanges(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterchanges

        NEEDS TESTING
        '''
        return self._call('eth_getFilterChanges', [filter_id])

    def eth_getFilterLogs(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs

        NEEDS TESTING
        '''
        return self._call('eth_getFilterLogs', [filter_id])

    def eth_getLogs(self, filter_object):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getlogs

        NEEDS TESTING
        '''
        return self._call('eth_getLogs', [filter_object])

    def eth_getWork(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getwork

        TESTED
        '''
        return self._call('eth_getWork')

    def eth_submitWork(self, nonce, header, mix_digest):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submitwork

        NEEDS TESTING
        '''
        return self._call('eth_submitWork', [nonce, header, mix_digest])

    def eth_submitHashrate(self, hash_rate, client_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submithashrate

        NEEDS TESTING
        '''
        return self._call('eth_submitHashrate', [hash_rate, client_id])

    def db_putString(self, db_name, key, value):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_putstring

        TESTED
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_putString', [db_name, key, value])

    def db_getString(self, db_name, key):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_getstring

        TESTED
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_getString', [db_name, key])

    def db_putHex(self, db_name, key, value):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_puthex

        TESTED
        '''
        if not value.startswith('0x'):
            value = '0x{}'.format(value)
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_putHex', [db_name, key, value])

    def db_getHex(self, db_name, key):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_gethex

        TESTED
        '''
        warnings.warn('deprecated', DeprecationWarning)
        return self._call('db_getHex', [db_name, key])

    def shh_post(self, topics, payload, priority, ttl, _from=None, to=None):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_post

        NEEDS TESTING
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

        N/A
        '''
        return self._call('shh_version')

    def shh_newIdentity(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newidentity

        N/A
        '''
        return self._call('shh_newIdentity')

    def shh_hasIdentity(self, address):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_hasidentity

        NEEDS TESTING
        '''
        return self._call('shh_hasIdentity', [address])

    def shh_newGroup(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newgroup

        N/A
        '''
        return self._call('shh_newGroup')

    def shh_addToGroup(self):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_addtogroup

        NEEDS TESTING
        '''
        return self._call('shh_addToGroup')

    def shh_newFilter(self, to, topics):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newfilter

        NEEDS TESTING
        '''
        _filter = {
            'to':     to,
            'topics': topics,
        }
        return self._call('shh_newFilter', [_filter])

    def shh_uninstallFilter(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_uninstallfilter

        NEEDS TESTING
        '''
        return self._call('shh_uninstallFilter', [filter_id])

    def shh_getFilterChanges(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getfilterchanges

        NEEDS TESTING
        '''
        return self._call('shh_getFilterChanges', [filter_id])

    def shh_getMessages(self, filter_id):
        '''
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getmessages

        NEEDS TESTING
        '''
        return self._call('shh_getMessages', [filter_id])
