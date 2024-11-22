#!/bin/bash

curl -H "Content-Type: application/json" \
     --request POST \
     --data '{"service": "ipfs", "data": "bafyreidykglsfhoixmivffc5uwhcgshx4j465xwqntbmu43nb2dzqwfvae", "keypath": "", "abi": "cbor", "multiplier": "10000000000000000000", "refundTo": "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266"}' http://localhost:8000/api1-handler


