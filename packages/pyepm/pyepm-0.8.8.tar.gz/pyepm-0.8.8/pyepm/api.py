#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: jorisbontje
# @Date:   2014-08-03 13:53:04
# @Last Modified by:   caktux
# @Last Modified time: 2015-02-25 17:50:15

import json
import logging
import requests
import sys
import time
from uuid import uuid4

from pyethereum import abi
from serpent import get_prefix, decode_datalist
from utils import unhex

logger = logging.getLogger(__name__)

def abi_data(fun_name, sig, data):
    types = []
    prefix = get_prefix(fun_name, sig)
    data_abi = hex(prefix)

    for i, s in enumerate(sig):
        if s == 's':
            types.append('string')
        elif s == 'a':
            types.append('int256[]')
        else:
            if isinstance(data[i], (str, unicode)) and data[i][:2] == "0x":
                data[i] = unhex(data[i])
            types.append('int256')
    data_abi += abi.encode_abi(types, data).encode('hex')

    logger.debug("ABI data: %s" % data_abi)
    return data_abi

class ApiException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "code=%d, message=\"%s\"" % (self.code, self.message)


class Api(object):

    def __init__(self, config):
        self.host = config.get('api', 'host')
        self.port = config.getint('api', 'port')
        self.jsonrpc_url = "http://%s:%s" % (self.host, self.port)
        logger.debug("Deploying to %s" % self.jsonrpc_url)

        self.address = config.get("api", "address")
        self.gas = config.get("deploy", "gas")
        self.gas_price = config.get("deploy", "gas_price")

    def _rpc_post(self, method, params):
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": method,
            "params": params}
        headers = {'content-type': 'application/json'}

        r = requests.post(self.jsonrpc_url, data=json.dumps(payload), headers=headers)
        if r.status_code >= 400:
            raise ApiException(r.status_code, r.reason)

        response = r.json()

        logger.debug(response)

        if 'error' in response:
            raise ApiException(response['error']['code'], response['error']['message'])

        return response.get('result')

    def accounts(self):
        return self._rpc_post('eth_accounts', None)

    def balance_at(self, address):
        params = [address]
        balance = self._rpc_post('eth_balanceAt', params)
        return unhex(balance)

    def block(self, nr):
        params = [nr]
        return self._rpc_post('eth_blockByNumber', params)

    def defaultBlock(self):
        params = []
        return self._rpc_post('eth_defaultBlock', params)

    def setDefaultBlock(self, nr):
        params = [nr]
        return self._rpc_post('eth_setDefaultBlock', params)

    def transaction_count(self, address=None):
        if address is None:
            address = "0x" + self.address
        params = [address]
        return self._rpc_post('eth_countAt', params)

    def check(self, addresses):
        params = {
            'a': addresses
        }
        return self._rpc_post('check', params)

    def coinbase(self):
        return self._rpc_post('eth_coinbase', None)

    def create(self, code, from_=None, gas=None, gas_price=None, endowment=0):
        if not code.startswith('0x'):
            code = '0x' + code
        # params = [{'code': code}]

        if gas is None:
            gas = self.gas
        if gas_price is None:
            gas_price = self.gas_price
        if from_ is None:
            from_ = self.address

        params = [{
            'code': code,
            'from': from_,
            'gas': str(gas),
            'gasPrice': str(gas_price),
            'value': str(endowment)
        }]
        return self._rpc_post('eth_transact', params)

    def is_contract_at(self, address):
        params = [address]
        return unhex(self._rpc_post('eth_codeAt', params)) != 0

    def is_listening(self):
        return self._rpc_post('eth_listening', None)

    def is_mining(self):
        return self._rpc_post('eth_mining', None)

    def key(self):
        return self._rpc_post('key', None)

    def keys(self):
        return self._rpc_post('keys', None)

    def last_block(self):
        return self.block(-1)

    def lll(self, contract):
        params = {
            's': contract
        }
        return self._rpc_post('eth_lll', params)

    def number(self):
        return self._rpc_post('eth_number', None)

    def peer_count(self):
        return self._rpc_post('eth_peerCount', None)

    def state_at(self, address, index):
        params = [address, index]
        return self._rpc_post('eth_stateAt', params)

    def storage_at(self, address):
        params = [address]
        return self._rpc_post('eth_storageAt', params)

    def transact(self, dest, fun_name=None, sig='', data=None, gas=None, gas_price=None, value=0, from_=None):
        if not dest.startswith('0x'):
            dest = '0x' + dest

        if fun_name is not None:
            data = abi_data(fun_name, sig, data)

        if gas is None:
            gas = self.gas
        if gas_price is None:
            gas_price = self.gas_price
        if from_ is None:
            from_ = self.address

        params = [{
            'to': dest,
            'data': data,
            'gas': str(gas),
            'gasPrice': str(gas_price),
            'value': str(value)}]
        return self._rpc_post('eth_transact', params)

    def call(self, dest, fun_name, sig='', data=None, gas=None, gas_price=None, from_=None):
        if not dest.startswith('0x'):
            dest = '0x' + dest

        if fun_name is not None:
            data = abi_data(fun_name, sig, data)

        if gas is None:
            gas = self.gas
        if gas_price is None:
            gas_price = self.gas_price
        if from_ is None:
            from_ = self.address

        params = [{
            'to': dest,
            'data': data,
            'gas': str(gas),
            'gasPrice': str(gas_price)}]
        r = self._rpc_post('eth_call', params)
        return decode_datalist(r[2:].decode('hex'))

    def wait_for_transaction(self, from_count=None, verbose=False):
        self.setDefaultBlock(0)

        if from_count is None:
            time.sleep(1)
            return

        if verbose:
            sys.stdout.write('Waiting for transaction')
            start_time = time.time()

        while True:
            if verbose:
                sys.stdout.write('.')
                sys.stdout.flush()
            time.sleep(1)
            to_count = self.transaction_count()
            if to_count > from_count:
                break

        if verbose:
            delta = time.time() - start_time
            logger.info(" took %ds" % delta)

    def wait_for_contract(self, address=None, verbose=False):
        self.setDefaultBlock(0)

        if verbose:
            sys.stdout.write('Waiting for contract at %s' % address)
            start_time = time.time()

        while True:
            if verbose:
                sys.stdout.write('.')
                sys.stdout.flush()
            time.sleep(1)
            codeat = self.is_contract_at(address)
            if codeat:
                break

        if verbose:
            delta = time.time() - start_time
            logger.info(" took %ds" % delta)

    def wait_for_next_block(self, verbose=False):
        if verbose:
            sys.stdout.write('Waiting for next block to be mined')
            start_time = time.time()

        last_block = self.last_block()
        while True:
            if verbose:
                sys.stdout.write('.')
                sys.stdout.flush()
            time.sleep(5)
            block = self.last_block()
            if block != last_block:
                break

        if verbose:
            delta = time.time() - start_time
            logger.info("Ready! Mining took %ds" % delta)
