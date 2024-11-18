#!/usr/bin/env python3

import logging
import os
import re
import requests
import eth_utils
import cbor2
import eth_abi
import uvicorn
import ipfs_api
import ipfshttpclient2
from fastapi import Request, FastAPI

from executor.fees import get_fee

app = FastAPI()
logger = logging.getLogger('uvicorn.error')
api_adapter = os.getenv('TRUFLATION_API_HOST', 'http://api-adapter:8081')
ipfs_host = os.getenv('IPFS_HOST', '/dns/localhost/tcp/5001/http')

def ipfs_connect():
    logger.debug(ipfs_host)
    return ipfshttpclient2.client.connect(ipfs_host)

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

@app.get("/hello")
def hello_world():
    return "<h2>Hello, World!</h2>"


async def process_request_api1(content, handler):
    logger.debug(content)
    oracle_request = content['meta']['oracleRequest']
    log_data = oracle_request['data']
    request_id = oracle_request['requestId']
    payment = int(oracle_request['payment'])
    cbor_bytes = bytes.fromhex("bf" + log_data[2:] + "ff")
    obj = cbor2.loads(cbor_bytes)
    logger.debug(obj)
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
        content = await handler(obj)
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
    return {
        "tx0": encode_tx,
        "tx1": process_refund
    }

async def json_handler(obj):
    if obj['service'] == 'ping':
        return obj['data']
    if obj['service'] == 'ipfs':
        logger.debug('processing IPFS')
        ipfs_client = ipfs_connect()
        data = ipfs_client.dag.get(obj['data'])
        logger.debug(data)
        return data
    r = requests.post(api_adapter, json=obj)
    return r.content

@app.post("/api1")
async def api1(request: Request):
    return await process_request_api1(await request.json(), json_handler)

@app.post("/api1-handler")
async def api1_handler(request: Request):
    return await json_handler(await request.json())

@app.post("/api1-test")
async def api1_test(request: Request):
    async def handler(obj):
        return obj.get('data', '')
    return await process_request_api1(await request.json(), handler)


@app.post("/api0")
async def api0(request: Request):
    content = await request.json()
    logger.debug(content)
    oracle_request = content['meta']['oracleRequest']
    log_data = oracle_request['data']
    request_id = oracle_request['requestId']
    b = bytes.fromhex("bf" + log_data[2:] + "ff")
    o = cbor2.loads(b)
    logger.debug(o)
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
    logger.debug(encode_tx)
    return encode_tx


@app.post("/api-adapter")
async def process_api_adapter(request: Request):
    content = await request.json()
    r = requests.post(api_adapter, json=content)
    return r.content

def create_app():
    return app

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', log_level="debug")
