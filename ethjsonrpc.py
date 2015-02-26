# © Christian Lundkvist
import json
import httplib
import serpent

def jsonrpc_query(host, port, query, id_string = ''):

    complete_query = query.copy()
    complete_query.update({'id' : id_string, 'jsonrpc' : '2.0'})
    params = json.JSONEncoder().encode(complete_query)
    
    conn = httplib.HTTPConnection(host, port)
    conn.request("POST", "", params)

    resp = conn.getresponse()
    response_object = resp.read().decode()
    response_dict = json.loads(response_object)
    conn.close()
    
    return response_dict


class EthJsonRpc:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def call(self, method, params):
        resp = jsonrpc_query(self.host, self.port, {'method' : method, 'params' : params})

        if 'result' in resp:
            return resp['result']
        else:
            raise RuntimeError('Error from RPC call: ' + str(resp))

    def send_tx_abi(self, to, funid, abi, value, from_addr=None, gas=None, gas_price=None):
        data = '0x' + '{0:02x}'.format(funid)
        if isinstance(abi, list):
            for d in abi:
                if (len(d) < 64):
                    data += '0' * (64 - len(d)) + d
                else:
                    data += d
        else:
            raise RuntimeError('Transaction ABI must be a list')

        tx_params = {'to' : to,
                     'data' : data,
                     'from' : from_addr,
                     'gas' : gas,
                     'gasPrice' : gas_price,
                     'value' : str(value)
                     }
            
        return self.call('eth_transact', [tx_params])

    def make_call(self, to, funid, abi, value, from_addr=None, gas=None, gas_price=None):
        data = '0x' + '{0:02x}'.format(funid)
        if isinstance(abi, list):
            for d in abi:
                if (len(d) < 64):
                    data += '0' * (64 - len(d)) + d
                else:
                    data += d
        else:
            raise RuntimeError('Transaction ABI must be a list')

        tx_params = {'to' : to,
                     'data' : data,
                     'from' : from_addr,
                     'gas' : gas,
                     'gasPrice' : gas_price,
                     'value' : str(value)
                     }
            
        return self.call('eth_call', [tx_params])

    def send_tx(self, destination, msg, value, from_addr=None, gas=None, gas_price=None):

        data = '0x'
        if isinstance(msg, list):
            for d in msg:
                if (len(d) < 64):
                    data += '0' * (64 - len(d)) + d
                else:
                    data += d
        elif isinstance(msg, str):
            data = msg
        else:
            raise RuntimeError('Unsupported message type in send_tx')

        tx_params = {'to' : destination,
                     'data' : data,
                     'from' : from_addr,
                     'gas' : gas,
                     'gasPrice' : gas_price,
                     'value' : str(value)
                     }
            
        return self.call('eth_transact', [tx_params])

    def create_contract(self, serpent_code, endowment, from_addr=None, gas=None, gas_price=None):

        byte_code = '0x' + serpent.compile(serpent_code).encode('hex')

        contract_params = {'to' : None,
                           'from' : from_addr,
                           'data' : byte_code,
                           'value' : str(endowment),
                           'gas' : gas,
                           'gasPrice' : gas_price
                           }
            
        return self.call('eth_transact', [contract_params])
