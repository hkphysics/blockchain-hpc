#!/bin/bash
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
cd $SCRIPT_DIR/..
mkdir -p log
rm -f state/state.json
docker compose down
docker volume rm blockchain-hpc_pg_data
docker volume rm blockchain-hpc_hardhat_state
docker compose up >& log/blockchain.log &
sleep 60
$SCRIPT_DIR/populate-cl.sh
