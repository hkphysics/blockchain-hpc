#!/usr/bin/env python3

import logging
import os
import re
import requests
import eth_utils
import cbor2
import eth_abi
from flask import Flask, request, jsonify
from tfi_orders.fees import get_fee

app = Flask(__name__)
api_adapter = os.getenv('TRUFLATION_API_HOST', 'http://api-adapter:8081')

def decode_response(content):
    content_str =  content.decode('utf-8') if hasattr(content, 'decode') \
        else content
    if re.match('^0x[A-Fa-f0-9]+$', content_str):
        return from_hex(content_str)
    return content

def encode_function(signature, parameters):
    params_list = signature.split("(")[1]
    param_types = params_list.replace(")", "").replace(" ", "").split(",")
    func_sig = eth_utils.function_signature_to_4byte_selector(
        signature
    )
    encode_tx = eth_abi.encode(param_types, parameters)
    return "0x" + func_sig.hex() + encode_tx.hex()

def from_hex(x):
    return bytes.fromhex(x[2:])

def refund_address(obj, default):
    refund_addr = obj.get('refundTo', None)
    if refund_addr is None or not eth_utils.is_hex_address(refund_addr):
        refund_addr = default
    return refund_addr

@app.route("/hello")
def hello_world():
    return "<h2>Hello, World!</h2>"


def process_request_api1(content, handler):
    app.logger.debug(content)
    oracle_request = content['meta']['oracleRequest']
    log_data = oracle_request['data']
    request_id = oracle_request['requestId']
    payment = int(oracle_request['payment'])
    cbor_bytes = bytes.fromhex("bf" + log_data[2:] + "ff")
    obj = cbor2.loads(cbor_bytes)
    app.logger.debug(obj)
    encode_tx = None
    encode_large = None
    fee = get_fee(obj)
    # should reject request but some networks require polling
    if payment < fee:
        """
        encode_tx = encode_function(
            'rejectOracleRequest(bytes32,uint256,address,bytes4,uint256,address)', [
                from_hex(request_id),
                int(oracle_request['payment']),
                from_hex(oracle_request['callbackAddr']),
                from_hex(oracle_request['callbackFunctionId']),
                int(oracle_request['cancelExpiration']),
                from_hex(oracle_request['callbackAddr'])
            ])
        """
        encode_large = eth_abi.encode(
            ['bytes32', 'bytes'],
            [from_hex(request_id),
             b'{"error": "fee too small"}']
        )
        encode_tx = encode_function(
            'fulfillOracleRequest2AndRefund(bytes32,uint256,address,bytes4,uint256,bytes,uint256)', [
                from_hex(request_id),
                int(oracle_request['payment']),
                from_hex(oracle_request['callbackAddr']),
                from_hex(oracle_request['callbackFunctionId']),
                int(oracle_request['cancelExpiration']),
                encode_large,
                payment
            ])
    else:
        content = handler(obj)
        encode_large = eth_abi.encode(
            ['bytes32', 'bytes'],
            [from_hex(request_id),
             decode_response(content)]
        )
        encode_tx = encode_function(
            'fulfillOracleRequest2AndRefund(bytes32,uint256,address,bytes4,uint256,bytes,uint256)', [
                from_hex(request_id),
                int(oracle_request['payment']),
                from_hex(oracle_request['callbackAddr']),
                from_hex(oracle_request['callbackFunctionId']),
                int(oracle_request['cancelExpiration']),
                encode_large,
                payment - fee
            ])
    refund_addr = refund_address(obj, oracle_request['callbackAddr'])

    process_refund = encode_function(
        'processRefund(bytes32,address)',
        [
            from_hex(request_id),
            from_hex(refund_addr)
        ])
    return jsonify({
        "tx0": encode_tx,
        "tx1": process_refund
    })


@app.route("/api1", methods=['POST'])
def api1():
    def handler(obj):
        r = requests.post(api_adapter, json=obj)
        return r.content
    return process_request_api1(request.json, handler)


@app.route("/api1-test", methods=['POST'])
def api1_test():
    def handler(obj):
        return obj.get('data', '')
    return process_request_api1(request.json, handler)


@app.route("/api0", methods=['POST'])
def api0():
    content = request.json
    app.logger.debug(content)
    oracle_request = content['meta']['oracleRequest']
    log_data = oracle_request['data']
    request_id = oracle_request['requestId']
    b = bytes.fromhex("bf" + log_data[2:] + "ff")
    o = cbor2.loads(b)
    app.logger.debug(o)
    r = requests.post(api_adapter, json=o)
    encode_large = encode_abi(
        ['bytes32', 'bytes'],
        [from_hex(request_id),
         r.content]
    )
    encode_tx = encode_function(
        'fulfillOracleRequest2(bytes32,uint256,address,bytes4,uint256,bytes)', [
            from_hex(request_id),
            int(oracle_request['payment']),
            from_hex(oracle_request['callbackAddr']),
            from_hex(oracle_request['callbackFunctionId']),
            int(oracle_request['cancelExpiration']),
            encode_large
        ])
    app.logger.debug(encode_tx)
    return encode_tx


@app.route("/api-adapter", methods=['POST'])
def process_api_adapter():
    content = request.json
    r = requests.post(api_adapter, json=content)
    return r.content

if os.getenv('TFI_ORDERS_LOCAL_LOGLEVEL') is None:
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    app.logger.setLevel(os.getenv('TFI_ORDERS_LOCAL_LOGLEVEL'))

app.logger.info(f'Connecting to adapter at {api_adapter}')


def create_app():
    return app
