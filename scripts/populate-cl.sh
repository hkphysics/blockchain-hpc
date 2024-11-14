#!/bin/bash
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
cd $SCRIPT_DIR
source $SCRIPT_DIR/local-addresses.sh
docker compose exec link-main-node chainlink admin login -f /chainlink/.api
docker compose exec link-main-node chainlink admin status
docker compose exec link-main-node chainlink bridges create '{
  "name": "executor",
  "url": "http://executor:8000/api1",
  "confirmations": 1,
  "minimumContractPayment": "0"
}'
docker compose exec link-main-node chainlink jobs create /chainlink/chainnode/node-api1.toml

export NODE_ETH_ADDRESS=`docker compose exec link-main-node chainlink keys eth list | grep Address: | awk '{print $2}'`
npx hardhat run ./initialize-operator.ts --network localhost

