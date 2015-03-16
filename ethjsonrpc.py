# (C) Christian Lundkvist and Stefan George

from pyethereum.abi import ContractTranslator
import serpent
import requests
import json


class EthJsonRpc:

    def __init__(self, host, port, contract_code=None, contract_address=None):
        self.host = host
        self.port = port
        self.contract_code = None
        self.signature = None
        self.translation = None
        self.contract_address = contract_address
        self.update_code(contract_code)

    def update_code(self, contract_code):
        if contract_code:
            self.contract_code = contract_code
            self.signature = serpent.mk_full_signature(contract_code)
            self.translation = ContractTranslator(self.signature)

    def _call(self, method, params=None, _id=0):
        if params is None:
            params = []
        data = json.dumps({
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': _id
        })
        response = requests.post("http://{}:{}".format(self.host, self.port), data=data).json()
        return response['result']

    def create_contract(self, contract_code, value=0, from_address=None, gas=0, gas_price=0):
        self.update_code(contract_code)
        byte_code = serpent.compile(contract_code)
        self.contract_address = self.eth_transact(data=byte_code, value=value, from_address=from_address, gas=gas, gas_price=gas_price)
        return self.contract_address

    def eth_transact(self, to_address=None, function_name=None, data=None, value=0, from_address=None, gas=0, gas_price=0):
        if function_name:
            if data is None:
                data = []
            data = self.translation.encode(function_name, data)
        params = {
            'to': to_address,
            'data': '0x{}'.format(data.encode('hex')) if data else None,
            'from': from_address,
            'gas': hex(gas) if gas else None,
            'gasPrice': hex(gas_price) if gas_price else None,
            'value': hex(value) if value else None
        }
        response = self._call('eth_transact', [params])
        return response

    def eth_call(self, to_address, function_name, data=None):
        if data is None:
            data = []
        data = self.translation.encode(function_name, data)
        params = {
            'to': to_address,
            'data': '0x{}'.format(data.encode('hex'))
        }
        response = self._call('eth_call', [params])
        if function_name:
            response = self.translation.decode(function_name, response[2:].decode('hex'))
        return response

    def web3_sha3(self, data):
        data = str(data).encode('hex')
        return self._call('web3_sha3', [data])

    def eth_coinbase(self):
        return self._call('eth_coinbase')

    def eth_setCoinbase(self, data):
        return self._call('eth_setCoinbase', [data])

    def eth_listening(self):
        return self._call('eth_listening')

    def eth_setListening(self, data):
        return self._call('eth_setListening', [data])

    def eth_mining(self):
        return self._call('eth_mining')

    def eth_setMining(self, data):
        return self._call('eth_setMining', [data])

    def eth_gasPrice(self):
        return self._call('eth_gasPrice')

    def eth_accounts(self):
        return self._call('eth_accounts')

    def eth_peerCount(self):
        return self._call('eth_peerCount')

    def eth_defaultBlock(self):
        return self._call('eth_defaultBlock')

    def eth_setDefaultBlock(self, data):
        return self._call('eth_setDefaultBlock', [data])

    def eth_number(self):
        return self._call('eth_number')

    def eth_balanceAt(self, data):
        return self._call('eth_balanceAt', [data])

    def eth_stateAt(self, data):
        return self._call('eth_stateAt', [data])

    def eth_storageAt(self, data):
        return self._call('eth_storageAt', [data])

    def eth_countAt(self, data):
        return self._call('eth_countAt', [data])

    def eth_transactionCountByHash(self, data):
        return self._call('eth_transactionCountByHash', [data])

    def eth_transactionCountByNumber(self, data):
        return self._call('eth_transactionCountByNumber', [data])

    def eth_uncleCountByHash(self, data):
        return self._call('eth_uncleCountByHash', [data])

    def eth_uncleCountByNumber(self, data):
        return self._call('eth_uncleCountByNumber' [data])

    def eth_codeAt(self, data):
        return self._call('eth_codeAt', [data])

    def eth_flush(self):
        return self._call('eth_flush')

    def eth_blockByHash(self, data):
        return self._call('eth_blockByHash', [data])

    def eth_blockByNumber(self, data):
        return self._call('eth_blockByNumber', [data])

    def eth_transactionByHash(self, data):
        return self._call('eth_transactionByHash', [data])

    def eth_transactionByNumber(self, data):
        return self._call('eth_transactionByNumber', [data])

    def eth_uncleByHash(self, data):
        return self._call('eth_uncleByHash', [data])

    def eth_uncleByNumber(self, data):
        return self._call('eth_uncleByNumber', [data])

    def eth_compilers(self):
        return self._call('eth_compilers')

    def eth_lll(self, data):
        return self._call('eth_lll', [data])

    def eth_solidity(self, data):
        return self._call('eth_solidity', [data])

    def eth_serpent(self, data):
        return self._call('eth_serpent', [data])

    def eth_newFilter(self, data):
        return self._call('eth_newFilter', [data])

    def eth_newFilterString(self, data):
        return self._call('eth_newFilterString', [data])

    def eth_uninstallFilter(self, data):
        return self._call('eth_uninstallFilter', [data])

    def eth_changed(self, data):
        return self._call('eth_changed', [data])

    def eth_filterLogs(self, data):
        return self._call('eth_filterLogs', [data])

    def eth_logs(self, data):
        return self._call('eth_logs', [data])

    def eth_getWork(self):
        return self._call('eth_getWork')

    def eth_submitWork(self, data):
        return self._call('eth_submitWork', [data])

    def db_put(self, data):
        return self._call('db_put', [data])

    def db_get(self, data):
        return self._call('db_get', [data])

    def db_putString(self, data):
        return self._call('db_putString', [data])

    def db_getString(self, data):
        return self._call('db_getString', [data])

    def shh_post(self, data):
        return self._call('shh_post', [data])

    def shh_newIdentity(self):
        return self._call('shh_newIdentity')

    def shh_haveIdentity(self, data):
        return self._call('shh_haveIdentity', [data])

    def shh_newGroup(self, data):
        return self._call('shh_newGroup', [data])

    def shh_addToGroup(self, data):
        return self._call('shh_addToGroup', [data])

    def shh_newFilter(self, data):
        return self._call('shh_newFilter', [data])

    def shh_uninstallFilter(self, data):
        return self._call('shh_uninstallFilter', [data])

    def shh_changed(self, data):
        return self._call('shh_changed', [data])

    def shh_getMessages(self, data):
        return self._call('shh_getMessages', [data])
